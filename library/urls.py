from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.user_login, name='login'),
    path('books/', views.book_list, name='book_list'),
]    

    # Book Management

    # Book Management
    path('books/', views.book_list, name='book_list'),
    path("catalog/", views.public_books, name="public_books"),
    path('books/add/', views.add_book, name='add_book'),
    path('books/pdf/', views.books_pdf, name='books_pdf'),
    path('books/excel/', views.books_excel, name='books_excel'),
    path('books/edit/<int:book_id>/', views.edit_book, name='edit_book'),
    path('books/delete/<int:book_id>/', views.delete_book, name='delete_book'),

    # Student Management
    path('students/', views.student_list, name='student_list'),
    path('students/add/', views.add_student, name='add_student'),
    path('students/edit/<int:student_id>/', views.edit_student, name='edit_student'),
    path('students/delete/<int:student_id>/', views.delete_student, name='delete_student'),

    # Issue Book
    path('issue/', views.issue_list, name='issue_list'),
    path('issue/add/', views.add_issue, name='add_issue'),
    path('issue/return/<int:issue_id>/', views.return_book, name='return_book'),
]