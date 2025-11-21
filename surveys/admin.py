# surveys/admin.py
from django.contrib import admin
from django.http import HttpResponse
import csv
from django.utils.html import format_html


from .models import InstructionDoc, Question, ResponseSession, Answer, EvaluationRun




@admin.register(InstructionDoc)
class InstructionDocAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "version", "is_active", "open_pdf")
    list_filter = ("is_active",)
    search_fields = ("title",)

    def open_pdf(self, obj):
        if not obj.file:
            return "-"
        return format_html(
            '<a href="{}" target="_blank">Open PDF</a>',
            obj.file.url,
        )
    open_pdf.short_description = "PDF"



@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ("id", "key", "order", "is_active")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("text",)




class AnswerInline(admin.TabularInline):
    
    model = Answer
    extra = 0
    fields = ("question", "rating_int", "reason_text", "improvement_text")
    show_change_link = True


class ResponseSessionInline(admin.TabularInline):
    
    model = ResponseSession
    extra = 0
    fields = ("doc", "user_token", "started_at", "finished_at")
    readonly_fields = ("started_at", "finished_at")
    show_change_link = True




@admin.register(EvaluationRun)
class EvaluationRunAdmin(admin.ModelAdmin):
    
    list_display = ("id", "user_token", "total_steps", "created_at", "finished_at")
    list_filter = ("finished_at",)
    search_fields = ("user_token",)
    date_hierarchy = "created_at"
    inlines = [ResponseSessionInline]




@admin.register(ResponseSession)
class ResponseSessionAdmin(admin.ModelAdmin):
    list_display = ("id", "run", "doc", "open_doc_pdf", "user_token", "started_at", "finished_at")
    list_filter = ("doc", "run", "started_at", "finished_at")
    search_fields = ("user_token", "doc__title")
    inlines = [AnswerInline]

    def open_doc_pdf(self, obj):
        if not obj.doc or not obj.doc.file:
            return "-"
        return format_html(
            '<a href="{}" target="_blank">Open PDF</a>',
            obj.doc.file.url,
        )
    open_doc_pdf.short_description = "Document PDF"




def export_answers_to_csv(modeladmin, request, queryset):
    response = HttpResponse(content_type="text/csv")
    response["Content-Disposition"] = 'attachment; filename="answers.csv"'
    writer = csv.writer(response)
    writer.writerow([
        "answer_id",
        "session_id",
        "doc_title",
        "question_key",
        "rating",
        "reason_text",
        "improvement_text",
        "session_started_at",
        "session_finished_at",
        "user_token",
    ])

    qs = queryset.select_related("session", "question", "session__doc")
    for a in qs:
        writer.writerow([
            a.id,
            a.session_id,
            a.session.doc.title if a.session and a.session.doc_id else "",
            a.question.key if a.question_id else "",
            a.rating_int,
            (a.reason_text or "").replace("\r", " ").replace("\n", " "),
            (a.improvement_text or "").replace("\r", " ").replace("\n", " "),
            a.session.started_at if a.session_id else "",
            a.session.finished_at if a.session_id else "",
            a.session.user_token if a.session_id else "",
        ])
    return response

export_answers_to_csv.short_description = "Export selected answers to CSV"


@admin.register(Answer)
class AnswerAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "get_run_id",
        "get_doc_title",
        "question",
        "rating_int",
        "short_reason",
        "short_improvement",
        "get_user_token",
    )
    list_filter = ("rating_int", "question", "session__doc", "session__run")
    search_fields = ("reason_text", "improvement_text", "session__user_token", "session__doc__title")
    actions = [export_answers_to_csv]

    def get_run_id(self, obj):
        return obj.session.run_id if obj.session and obj.session.run_id else "-"
    get_run_id.short_description = "Run ID"

    def get_doc_title(self, obj):
        return obj.session.doc.title if obj.session and obj.session.doc_id else "-"
    get_doc_title.short_description = "Document"

    def get_user_token(self, obj):
        return obj.session.user_token if obj.session else "-"
    get_user_token.short_description = "User token"

    def short_reason(self, obj):
        return (obj.reason_text or "")[:60]
    short_reason.short_description = "Reason"

    def short_improvement(self, obj):
        return (obj.improvement_text or "")[:60]
    short_improvement.short_description = "Improvement"

