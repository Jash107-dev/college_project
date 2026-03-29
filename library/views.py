from django.shortcuts import render, redirect, get_object_or_404
from .models import Book

def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})


def add_book(request):
    if request.method == "POST":
        isbn = request.POST.get('isbn')

        if Book.objects.filter(isbn=isbn).exists():
            return render(request, 'library/add_book.html', {
                'error': 'A book with this ISBN already exists.'
            })

        Book.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            isbn=isbn,
            category=request.POST.get('category'),
            quantity=int(request.POST.get('quantity'))
        )
        return redirect('book_list')

    return render(request, 'library/add_book.html')


def update_book(request, id):
    book = get_object_or_404(Book, id=id)

    if request.method == 'POST':
        isbn = request.POST.get('isbn')

        # Allow same ISBN if it belongs to this book, block if it belongs to another
        if Book.objects.filter(isbn=isbn).exclude(id=id).exists():
            return render(request, 'library/update_book.html', {
                'book': book,
                'error': 'Another book with this ISBN already exists.'
            })

        book.title = request.POST['title']
        book.author = request.POST['author']
        book.isbn = isbn
        book.category = request.POST['category']
        book.quantity = int(request.POST.get('quantity'))
        book.save()
        return redirect('book_list')

    return render(request, 'library/update_book.html', {'book': book})


def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    book.delete()
    return redirect('book_list')