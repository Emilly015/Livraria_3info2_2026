from django.db import transaction
from rest_framework.serializers import CharField, ModelSerializer, SerializerMethodField

from core.models import Compra, ItensCompra


class ItensCompraCreateUpdateSerializer(ModelSerializer):
    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade')


class CompraCreateUpdateSerializer(ModelSerializer):
    itens = ItensCompraCreateUpdateSerializer(many=True)

    class Meta:
        model = Compra
        fields = ('id', 'usuario', 'itens')

    @transaction.atomic
    def create(self, validated_data):
        itens = validated_data.pop('itens')
        compra = Compra.objects.create(**validated_data)
        for item in itens:
            ItensCompra.objects.create(compra=compra, **item)
        compra.save()
        return compra


class ItensCompraSerializer(ModelSerializer):
    total = SerializerMethodField()

    def get_total(self, instance):
        return instance.livro.preco * instance.quantidade

    class Meta:
        model = ItensCompra
        fields = ('livro', 'quantidade', 'total')
        depth = 1


class CompraSerializer(ModelSerializer):
    itens = ItensCompraSerializer(many=True, read_only=True)
    status = CharField(source='get_status_display', read_only=True)
    usuario = CharField(source='usuario.email', read_only=True)
    fields = ('id', 'usuario', 'status', 'total', 'itens')

    class Meta:
        model = Compra
        fields = '__all__'
