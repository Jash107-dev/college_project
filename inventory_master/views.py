from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Inventory
from .forms import InventoryForm


@login_required
def item_list(request):
    items = Inventory.objects.all()
    return render(request, 'inventory_master/item_list.html', {'items': items})


@login_required
def add_item(request):
    if request.method == 'POST':
        form = InventoryForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('item_list')
    else:
        form = InventoryForm()
    return render(request, 'inventory_master/add_item.html', {'form': form})


@login_required
def update_item(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    form = InventoryForm(request.POST or None, instance=item)
    if form.is_valid():
        form.save()
        return redirect('item_list')
    return render(request, 'inventory_master/update_item.html', {'form': form})


@login_required
def delete_item(request, pk):
    item = get_object_or_404(Inventory, pk=pk)
    if request.method == 'POST':
        item.delete()
        return redirect('item_list')
    return render(request, 'inventory_master/delete_item.html', {'item': item})