# surveys/views.py
import os
import random
import re
import json
from django.contrib import messages

from django.http import JsonResponse
from django.views.decorators.http import require_POST
from django.views.decorators.csrf import csrf_exempt

from django.conf import settings
from django.urls import reverse
from django.http import (
    StreamingHttpResponse,
    FileResponse,
    Http404,
    HttpResponse,
    HttpResponseBadRequest,
)
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone

from .forms import EvaluationForm
from .models import Answer, InstructionDoc, Question, ResponseSession, RunProgress, EvaluationRun

COOKIE_UID = "uid"
QUEUE_KEY = "doc_queue_ids"
RESP_KEY = "resp_session_ids"
STEP_KEY = "current_step"


def _get_or_set_uid(request, response=None):
    uid = request.COOKIES.get(COOKIE_UID)
    if uid:
        return uid
    import secrets
    uid = secrets.token_hex(16)
    if response is not None:
        response.set_cookie(COOKIE_UID, uid, max_age=3600 * 24 * 365)
    return uid


def _restore_from_progress_if_any(request):
    uid = request.COOKIES.get(COOKIE_UID)
    if not uid:
        return False

    prog = RunProgress.objects.filter(
        user_token=uid,
        is_finished=False
    ).order_by("-updated_at").select_related("run").first()

    if not prog:
        return False

    resp_ids = prog.resp_session_ids
    docs = list(
        ResponseSession.objects.filter(id__in=resp_ids)
        .select_related("doc", "run")
        .order_by("id")
    )
    if not docs:
        return False

    request.session[QUEUE_KEY] = [s.doc_id for s in docs]
    request.session[RESP_KEY] = resp_ids
    request.session[STEP_KEY] = max(1, min(prog.current_step, prog.total_steps))
    request.session.modified = True
    return True


def home(request):
    uid = request.COOKIES.get(COOKIE_UID)
    resume_step = None
    if uid:
        prog = RunProgress.objects.filter(user_token=uid, is_finished=False).order_by("-updated_at").first()
        if prog:
            resume_step = prog.current_step
    return render(request, "surveys/home.html", {"resume_step": resume_step})


def start(request):
  
    if request.method != "POST":
       
        if _restore_from_progress_if_any(request):
            return redirect("surveys:evaluate", step=request.session.get(STEP_KEY, 1))
        return redirect("surveys:home")

    docs = list(InstructionDoc.objects.filter(is_active=True))
    if not docs:
        messages.error(request, "No instruction PDFs configured.")
        return redirect("surveys:home")

    
    k = min(5, len(docs))
    chosen = random.sample(docs, k=k)

    
    resp_ids: list[int] = []
    for d in chosen:
        sess = ResponseSession.objects.create(doc=d)
        resp_ids.append(sess.id)

    
    request.session[QUEUE_KEY] = [d.id for d in chosen]
    request.session[RESP_KEY] = resp_ids
    request.session[STEP_KEY] = 1
    request.session.modified = True

    
    resp = redirect("surveys:evaluate", step=1)
    uid = _get_or_set_uid(request, resp)

    
    run = EvaluationRun.objects.create(
        user_token=uid or "",
        total_steps=len(resp_ids),
    )
    
    ResponseSession.objects.filter(id__in=resp_ids).update(run=run)

    
    RunProgress.objects.update_or_create(
        user_token=uid,
        is_finished=False,
        defaults={
            "resp_session_ids": resp_ids,
            "current_step": 1,
            "total_steps": len(resp_ids),
        },
    )

    return resp




def evaluate(request, step: int):
    if not request.session.get(RESP_KEY):
        if not _restore_from_progress_if_any(request):
            return redirect("surveys:home")

    queue = request.session.get(QUEUE_KEY)
    resp_ids = request.session.get(RESP_KEY)
    if not queue or not resp_ids:
        messages.error(
            request,
            "Your evaluation session has expired or is invalid. "
            "Please start a new evaluation."
        )
        return redirect("surveys:home")

    if step < 1 or step > len(resp_ids):
        raise Http404("Invalid step")

    sess_id = resp_ids[step - 1]
    sess = get_object_or_404(ResponseSession, id=sess_id)

    questions = list(Question.objects.filter(is_active=True).order_by("order", "id"))
    has_errors = False  # <-- to tell the template that this POST failed

    if request.method == "POST":
        form = EvaluationForm(request.POST, questions=questions)
        if form.is_valid():
            for q in questions:
                rating = int(form.cleaned_data[f"rating_{q.id}"])
                reason = form.cleaned_data.get(f"reason_{q.id}", "").strip()
                improve = form.cleaned_data.get(f"improve_{q.id}", "").strip()
                Answer.objects.update_or_create(
                    session=sess,
                    question=q,
                    defaults={
                        "rating_int": rating,
                        "reason_text": reason,
                        "improvement_text": improve,
                    },
                )

            next_step = step + 1
            request.session[STEP_KEY] = next_step
            request.session.modified = True

            uid = request.COOKIES.get(COOKIE_UID, "")
            if uid:
                RunProgress.objects.update_or_create(
                    user_token=uid,
                    is_finished=False,
                    defaults={
                        "resp_session_ids": resp_ids,
                        "current_step": min(next_step, len(resp_ids)),
                        "total_steps": len(resp_ids),
                    },
                )

            if next_step > len(resp_ids):
                return redirect("surveys:done")
            return redirect("surveys:evaluate", step=next_step)
        else:
            # Form invalid: user clicked Next but there is a problem
            has_errors = True
            messages.error(
                request,
                "There was a problem with your answers. "
                "Please make sure every rating is a whole number from 1 to 7 and try again."
            )
    else:
        initial = {}
        existing = {a.question_id: a for a in Answer.objects.filter(session=sess)}
        for q in questions:
            a = existing.get(q.id)
            if a:
                initial[f"rating_{q.id}"] = a.rating_int
                initial[f"reason_{q.id}"] = a.reason_text or ""
                initial[f"improve_{q.id}"] = a.improvement_text or ""
        form = EvaluationForm(questions=questions, data=None, initial=initial)

    q_rows = [
        {
            "q": q,
            "rating": form[f"rating_{q.id}"],
            "reason": form[f"reason_{q.id}"],
            "improve": form[f"improve_{q.id}"],
        }
        for q in questions
    ]

    is_pdf_step = (step % 2 == 1)
    is_video_step = not is_pdf_step

    video_url = None
    video_title = None
    if is_video_step:
        if step == 2:
            video_url = reverse("surveys:stream_video", args=["video1_faststart.mp4"])
            video_title = "Product Manual – Video 1"
        elif step == 4:
            video_url = reverse("surveys:stream_video", args=["video2_faststart.mp4"])
            video_title = "Product Manual – Video 2"

    context = {
        "step": step,
        "total_steps": len(resp_ids),
        "sess": sess,
        "form": form,
        "q_rows": q_rows,
        "is_last": (step == len(resp_ids)),
        "is_pdf_step": is_pdf_step,
        "is_video_step": is_video_step,
        "video_url": video_url,
        "video_title": video_title,
        
    }
    return render(request, "surveys/evaluate.html", context)

def done(request):
    resp_ids = request.session.get(RESP_KEY)
    if not resp_ids:
        return redirect("surveys:home")

    sessions = list(
        ResponseSession.objects.filter(id__in=resp_ids)
        .select_related("doc", "run")
    )
    questions = list(Question.objects.filter(is_active=True).order_by("order", "id"))

    if request.method == "POST":
        now = timezone.now()
        uid = request.COOKIES.get(COOKIE_UID, "")

        
        for s in sessions:
            s.user_token = uid
            s.finished_at = now
            s.save(update_fields=["user_token", "finished_at"])

        
        run = sessions[0].run if sessions and sessions[0].run_id else None
        if run:
            run.user_token = uid or run.user_token
            run.finished_at = now
            run.total_steps = len(resp_ids)
            run.save(update_fields=["user_token", "finished_at", "total_steps"])

        
        if uid:
            RunProgress.objects.filter(
                user_token=uid,
                is_finished=False
            ).update(is_finished=True, updated_at=now, run=run if run else None)

        
        for k in (QUEUE_KEY, RESP_KEY, STEP_KEY):
            request.session.pop(k, None)
        request.session.modified = True
        return redirect("surveys:thanks")

    return render(
        request,
        "surveys/done.html",
        {"sessions": sessions, "questions": questions},
    )


def thanks(request):
    return render(request, "surveys/thanks.html")


def inline_pdf(request, pk: int):
    doc = get_object_or_404(InstructionDoc, pk=pk)
    file_path = doc.file.path
    if not file_path.lower().endswith(".pdf"):
        return HttpResponse("Not a PDF", status=400)
    with open(file_path, "rb") as f:
        data = f.read()
    resp = HttpResponse(data, content_type="application/pdf")
    resp["Content-Disposition"] = f'inline; filename="{os.path.basename(file_path)}"'
    return resp

@require_POST
def save_partial_answer(request, session_id: int, question_id: int):
    sess = get_object_or_404(ResponseSession, id=session_id)
    q = get_object_or_404(Question, id=question_id, is_active=True)

    try:
        payload = json.loads(request.body.decode("utf-8"))
    except Exception:
        return JsonResponse({"ok": False, "error": "bad_json"}, status=400)

    updates = {}
    if "rating" in payload and payload["rating"] not in (None, ""):
        try:
            r = int(payload["rating"])
        except Exception:
            return JsonResponse({"ok": False, "error": "invalid_rating"}, status=400)
        if r < 1 or r > 7:
            return JsonResponse({"ok": False, "error": "rating_out_of_range"}, status=400)
        updates["rating_int"] = r

    if "reason" in payload:
        updates["reason_text"] = (payload["reason"] or "").strip()

    if "improve" in payload:
        updates["improvement_text"] = (payload["improve"] or "").strip()

    if not updates:
        return JsonResponse({"ok": False, "error": "no_fields"}, status=400)

    Answer.objects.update_or_create(
        session=sess,
        question=q,
        defaults=updates,
    )
    return JsonResponse({"ok": True, "saved": list(updates.keys())})

def stream_video(request, filename: str):
    file_path = os.path.join(settings.MEDIA_ROOT, "videos", filename)
    if not os.path.exists(file_path):
        raise Http404("Video not found")

    file_size = os.path.getsize(file_path)
    content_type = "video/mp4"
    range_header = request.META.get("HTTP_RANGE", "").strip()
    range_match = re.match(r"bytes=(\d+)-(\d*)", range_header)

    if range_match:
        start = int(range_match.group(1))
        end_str = range_match.group(2)
        end = int(end_str) if end_str else file_size - 1
        end = min(end, file_size - 1)
        length = end - start + 1

        def file_iterator(path, offset, length, chunk_size=8192):
            with open(path, "rb") as f:
                f.seek(offset)
                remaining = length
                while remaining > 0:
                    chunk = f.read(min(chunk_size, remaining))
                    if not chunk:
                        break
                    yield chunk
                    remaining -= len(chunk)

        resp = StreamingHttpResponse(
            file_iterator(file_path, start, length),
            status=206,
            content_type=content_type,
        )
        resp["Content-Length"] = str(length)
        resp["Content-Range"] = f"bytes {start}-{end}/{file_size}"
        resp["Accept-Ranges"] = "bytes"
        return resp

    resp = FileResponse(open(file_path, "rb"), content_type=content_type)
    resp["Content-Length"] = str(file_size)
    resp["Accept-Ranges"] = "bytes"
    return resp
