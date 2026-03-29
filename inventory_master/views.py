# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from .models import Inventory
from .forms import InventoryForm


# LIST ITEMS
def item_list(request):
    items = Inventory.objects.all()
    return render(
        request,
        'inventory_master/item_list.html',
        {'items': items}
    )

# ADD ITEM
def add_item(request):

    if request.method == 'POST':

        form = InventoryForm(request.POST)

        if form.is_valid():

            form.save()

            return redirect('item_list')

    else:

        form = InventoryForm()

    return render(
        request,
        'inventory_master/add_item.html',
        {'form': form}
    )


# UPDATE ITEM
def update_item(request, pk):

    item = get_object_or_404(Inventory, pk=pk)

    form = InventoryForm(
        request.POST or None,
        instance=item
    )

    if form.is_valid():

        form.save()

        return redirect('item_list')

    return render(
        request,
        'inventory_master/update_item.html',
        {'form': form}
    )


# DELETE ITEM
def delete_item(request, pk):

    item = get_object_or_404(Inventory, pk=pk)

    if request.method == 'POST':

        item.delete()

        return redirect('item_list')

    return render(
        request,
        'inventory_master/delete_item.html',
        {'item': item}
    )