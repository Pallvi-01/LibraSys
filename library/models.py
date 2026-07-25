from django.db import models


class Book(models.Model):

    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    isbn = models.CharField(max_length=20, unique=True)
    cover = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    category = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)
    available = models.PositiveIntegerField(default=1)
    added_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title


class Student(models.Model):

    name = models.CharField(max_length=100)
    roll_number = models.CharField(max_length=30, unique=True)
    course = models.CharField(max_length=100)
    mobile = models.CharField(max_length=15)
    email = models.EmailField()
    joined_on = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class IssueBook(models.Model):

    book = models.ForeignKey(Book, on_delete=models.CASCADE)

    student = models.ForeignKey(Student, on_delete=models.CASCADE)

    issue_date = models.DateField(auto_now_add=True)

    return_date = models.DateField()

    returned = models.BooleanField(default=False)

    fine = models.PositiveIntegerField(default=0)

    def __str__(self):
        return f"{self.book} - {self.student}"


class BookRequest(models.Model):

    book = models.ForeignKey(
        Book,
        on_delete=models.CASCADE
    )

    name = models.CharField(max_length=100)

    mobile = models.CharField(max_length=15)

    email = models.EmailField()

    requested_on = models.DateTimeField(
        auto_now_add=True
    )

    approved = models.BooleanField(
        default=False
    )

    def __str__(self):
        return f"{self.name} - {self.book.title}"