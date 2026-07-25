from django.contrib import admin
from .models import Book, Student, IssueBook, BookRequest


admin.site.register(Book)
admin.site.register(Student)
admin.site.register(IssueBook)
admin.site.register(BookRequest)