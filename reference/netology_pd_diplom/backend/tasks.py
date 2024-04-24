from celery import shared_task
from requests import get
from yaml import Loader
from yaml import load as load_yaml
from django.core.mail import EmailMultiAlternatives

from backend.models import Category, Parameter, Product, ProductInfo, ProductParameter, Shop


@shared_task()
def send_email(title, message,  from_email, email,):
    msg = EmailMultiAlternatives(
        subject=title,
        body=message,
        from_email=from_email,
        to=email
    )
    msg.send()


@shared_task()
def do_import(url, user_id):
    stream = get(url).content
    try:
        data = load_yaml(stream=stream, Loader=Loader)
        shop = data['shop']
        categories = data['categories']
        goods = data['goods']

    except Exception as err:
        return False
    shop, _ = Shop.objects.get_or_create(name=shop, user_id=user_id)
    for category in categories:
        category_object, _ = Category.objects.get_or_create(id=category['id'], name=category['name'])
        category_object.shops.add(shop.id)
        category_object.save()
    ProductInfo.objects.filter(shop_id=shop.id).delete()
    for item in goods:
        product, _ = Product.objects.get_or_create(name=item['name'], category_id=item['category'])

        product_info = ProductInfo.objects.create(product_id=product.id,
                                                  external_id=item['id'],
                                                  model=item['model'],
                                                  price=item['price'],
                                                  price_rrc=item['price_rrc'],
                                                  quantity=item['quantity'],
                                                  shop_id=shop.id)

        for name, value in item['parameters'].items():
            parameter_object, _ = Parameter.objects.get_or_create(name=name)
            ProductParameter.objects.create(product_info_id=product_info.id,
                                            parameter_id=parameter_object.id,
                                            value=value)
    return True