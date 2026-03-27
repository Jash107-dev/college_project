from django.shortcuts import render

# Create your views here.
from django.shortcuts import render, redirect
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
def update_item(request, id):

    item = Inventory.objects.get(id=id)

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
def delete_item(request, id):

    item = Inventory.objects.get(id=id)

    item.delete()

    return redirect('item_list')