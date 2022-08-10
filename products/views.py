from django.shortcuts import get_list_or_404, get_object_or_404
from django.db.models import Q
from rest_framework import views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from products.models import Product, Funding
from products.serializers import ProductListSerializer, ProductCreateSerializer, ProductDetailSerializer
from products.utils import RequestHandler
from users.permissions import IsOwnerOrReadOnly, ProductIsOwnerOrReadOnly


class ProductListViews(views.APIView, RequestHandler):
    permission_classes = [IsAuthenticatedOrReadOnly, IsOwnerOrReadOnly]

    def get(self, request):
        """ GET api/products """
        query = Q()
        search, sort = self._request_param(request)

        if search:
            # 파라미터 중 search가 있을 때, 상품명 like 검색
            query &= Q(name__icontains=search)

        products = Product.objects.filter(query)

        if sort:
            # 파라미터 중 sort가 있을 때, 상품 목록 정렬
            products = products.order_by(sort)

        serializer = ProductListSerializer(products, many=True)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def post(self, request):
        """ POST api/products """
        request.data['user'] = request.user.id
        serializer = ProductCreateSerializer(data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProductDetailView(views.APIView):
    permission_classes = [IsAuthenticatedOrReadOnly, ProductIsOwnerOrReadOnly]

    def get_object(self, pk):
        return get_object_or_404(Product, id=pk)

    def get(self, request, pk):
        """ GET api/products/:pk """
        product = self.get_object(pk)
        serializer = ProductDetailSerializer(product)

        return Response(serializer.data, status=status.HTTP_200_OK)

    def put(self, request, pk):
        """ PUT api/products/:pk """
        product = self.get_object(pk)
        serializer = ProductDetailSerializer(product, data=request.data)

        if serializer.is_valid():
            serializer.save()

            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        """ DELETE api/products/:pk """
        product = self.get_object(pk)

        if product is not None:
            product.delete()

            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(status=status.HTTP_400_BAD_REQUEST)
