from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Book


@login_required
def book_list(request):
    books = Book.objects.all()
    return render(request, 'library/book_list.html', {'books': books})


@login_required
def add_book(request):
    if request.method == "POST":
        isbn = request.POST.get('isbn')
        if Book.objects.filter(isbn=isbn).exists():
            return render(request, 'library/add_book.html', {
                'error': 'A book with this ISBN already exists.'
            })
        quantity_str = (request.POST.get('quantity', '0') or '0').strip()
        Book.objects.create(
            title=request.POST.get('title'),
            author=request.POST.get('author'),
            isbn=isbn,
            category=request.POST.get('category'),
            quantity=int(quantity_str or '0')
        )
        return redirect('book_list')
    return render(request, 'library/add_book.html')


@login_required
def update_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        isbn = request.POST.get('isbn')
        if Book.objects.filter(isbn=isbn).exclude(id=id).exists():
            return render(request, 'library/update_book.html', {
                'book': book,
                'error': 'Another book with this ISBN already exists.'
            })
        quantity_str = (request.POST.get('quantity', '0') or '0').strip()
        book.title = request.POST['title']
        book.author = request.POST['author']
        book.isbn = isbn
        book.category = request.POST['category']
        book.quantity = int(quantity_str or '0')
        book.save()
        return redirect('book_list')
    return render(request, 'library/update_book.html', {'book': book})


@login_required
def delete_book(request, id):
    book = get_object_or_404(Book, id=id)
    if request.method == 'POST':
        book.delete()
        return redirect('book_list')
    return render(request, 'library/delete_book.html', {'book': book})