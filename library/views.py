from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Student, IssueBook
from django.contrib.auth.decorators import login_required
from datetime import date
from django.http import HttpResponse
from reportlab.pdfgen import canvas
from reportlab.lib.units import inch
from openpyxl import Workbook
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import authenticate, login


@login_required
def dashboard(request):

    total_books = Book.objects.count()

    total_students = Student.objects.count()

    total_issued = IssueBook.objects.filter(returned=False).count()

    available_books = sum(book.available for book in Book.objects.all())

    recent_issues = IssueBook.objects.select_related(
        "book", "student"
    ).order_by("-issue_date")[:5]

    context = {
        "total_books": total_books,
        "total_students": total_students,
        "total_issued": total_issued,
        "available_books": available_books,
        "recent_issues": recent_issues,
        "pie_available": available_books,
        "pie_issued": total_issued,
    }

    return render(request, "library/dashboard.html", context)


# ---------------- BOOKS ---------------- #
@login_required
@user_passes_test(lambda u: u.is_staff)
def book_list(request):

    search = request.GET.get("search")

    if search:
        books = Book.objects.filter(
            title__icontains=search
        )
    else:
        books = Book.objects.all()

    return render(request, "library/book_list.html", {
        "books": books
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_book(request):

    if request.method == "POST":

        Book.objects.create(
            title=request.POST["title"],
            author=request.POST["author"],
            category=request.POST["category"],
            isbn=request.POST["isbn"],
            quantity=request.POST["quantity"],
            available=request.POST["quantity"],
            cover=request.FILES.get("cover")
        )

        return redirect("book_list")

    return render(request, "library/add_book.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_book(request, book_id):

    book = get_object_or_404(Book, id=book_id)

    if request.method == "POST":

        issued = book.quantity - book.available

        book.title = request.POST["title"]
        book.author = request.POST["author"]
        book.category = request.POST["category"]
        book.isbn = request.POST["isbn"]
        book.quantity = int(request.POST["quantity"])
        book.available = max(book.quantity - issued, 0)
        if request.FILES.get("cover"):
            book.cover = request.FILES["cover"]

        book.save()

        return redirect("book_list")

    return render(request, "library/edit_book.html", {
        "book": book
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_book(request, book_id):

    book = get_object_or_404(Book, id=book_id)
    book.delete()

    return redirect("book_list")


# ---------------- STUDENTS ---------------- #
@login_required
@user_passes_test(lambda u: u.is_staff)
def student_list(request):

    search = request.GET.get("search")

    if search:
        students = Student.objects.filter(name__icontains=search)
    else:
        students = Student.objects.all()

    return render(request, "library/student_list.html", {
        "students": students
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_student(request):

    if request.method == "POST":

        Student.objects.create(
            name=request.POST["name"],
            roll_number=request.POST["roll"],
            course=request.POST["course"],
            mobile=request.POST["mobile"],
            email=request.POST["email"]
        )

        return redirect("student_list")

    return render(request, "library/add_student.html")

@login_required
@user_passes_test(lambda u: u.is_staff)
def edit_student(request, student_id):

    student = get_object_or_404(Student, id=student_id)

    if request.method == "POST":

        student.name = request.POST["name"]
        student.roll_number = request.POST["roll"]
        student.course = request.POST["course"]
        student.mobile = request.POST["mobile"]
        student.email = request.POST["email"]

        student.save()

        return redirect("student_list")

    return render(request, "library/edit_student.html", {
        "student": student
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def delete_student(request, student_id):

    student = get_object_or_404(Student, id=student_id)
    student.delete()

    return redirect("student_list")


# ---------------- ISSUE BOOK ---------------- #
@login_required
@user_passes_test(lambda u: u.is_staff)
def issue_list(request):

    from datetime import date

    issues = IssueBook.objects.all()

    today = date.today()

    return render(request, "library/issue_list.html", {
        "issues": issues,
        "today": today
    })

@login_required
@user_passes_test(lambda u: u.is_staff)
def add_issue(request):

    if request.method == "POST":

        book = Book.objects.get(id=request.POST["book"])
        student = Student.objects.get(id=request.POST["student"])

        IssueBook.objects.create(
            book=book,
            student=student,
            return_date=request.POST["return_date"]
        )

        book.available -= 1
        book.save()

        return redirect("issue_list")

    return render(request, "library/add_issue.html", {
        "books": Book.objects.filter(available__gt=0),
        "students": Student.objects.all()
    })



@login_required
@user_passes_test(lambda u: u.is_staff)
def return_book(request, issue_id):

    issue = get_object_or_404(IssueBook, id=issue_id)

    if not issue.returned:

        today = date.today()

        # Late days calculate
        late_days = (today - issue.return_date).days

        if late_days > 0:
            issue.fine = late_days * 10      # ₹10 per day
        else:
            issue.fine = 0

        issue.returned = True
        issue.save()

        # Increase available books
        book = issue.book
        book.available += 1
        book.save()

    return redirect("issue_list")
   
@login_required
@user_passes_test(lambda u: u.is_staff)
def books_pdf(request):

    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="Books_Report.pdf"'

    p = canvas.Canvas(response)

    p.setFont("Helvetica-Bold", 18)
    p.drawString(180, 800, "LibraSys - Books Report")

    p.setFont("Helvetica-Bold", 12)
    p.drawString(40, 760, "Title")
    p.drawString(220, 760, "Author")
    p.drawString(360, 760, "Available")

    y = 735

    books = Book.objects.all()

    p.setFont("Helvetica", 11)

    for book in books:

        p.drawString(40, y, str(book.title))
        p.drawString(220, y, str(book.author))
        p.drawString(380, y, str(book.available))

        y -= 22

        if y < 60:
            p.showPage()
            y = 800

    p.save()

    return response

@login_required
@user_passes_test(lambda u: u.is_staff)
def books_excel(request):

    workbook = Workbook()

    sheet = workbook.active
    sheet.title = "Books Report"

    sheet.append([
        "Title",
        "Author",
        "Category",
        "ISBN",
        "Quantity",
        "Available"
    ])

    books = Book.objects.all()

    for book in books:

        sheet.append([
            book.title,
            book.author,
            book.category,
            book.isbn,
            book.quantity,
            book.available
        ])

    response = HttpResponse(
        content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
    )

    response["Content-Disposition"] = 'attachment; filename="Books_Report.xlsx"'

    workbook.save(response)

    return response   
    
def public_books(request):

    search = request.GET.get("search")

    if search:
        books = Book.objects.filter(
            title__icontains=search,
            available__gt=0
        )
    else:
        books = Book.objects.filter(
            available__gt=0
        )

    return render(request, "library/public_books.html", {
        "books": books
    })


def user_login(request):

    if request.method == "POST":

        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect("dashboard")

    return render(request, "library/login.html")