from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from pets.models import Pet
from pets.serializers import PetSerializer
from groups.models import Group
from traits.models import Trait


class PetView(APIView, PageNumberPagination):

    def post(self, request):
        serializer = PetSerializer(data=request.data)

        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group")
        traits_data = serializer.validated_data.pop("traits")

        try:
            group = Group.objects.get(scientific_name=group_data["scientific_name"])
        except Group.DoesNotExist:
            group = Group.objects.create(**group_data)

        pet = Pet.objects.create(**serializer._validated_data, group=group)

        for trait in traits_data:

            trait_obj = Trait.objects.filter(
                name__iexact=trait["name"]
            ).first()

            if not trait_obj:
                trait_obj = Trait.objects.create(**trait)

            pet.traits.add(trait_obj)
            pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data, 201)

    def get(self, request):
        pets = Pet.objects.all()

        result_page = self.paginate_queryset(pets, request, view=self)

        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)
