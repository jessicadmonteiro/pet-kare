from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.pagination import PageNumberPagination
from pets.models import Pet
from pets.serializers import PetSerializer
from groups.models import Group
from traits.models import Trait
from django.shortcuts import get_object_or_404


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

        trait_name = request.query_params.get("trait", None)

        traits = Trait.objects.filter(name=trait_name).first()
        pets = Pet.objects.filter(traits=traits).all()

        result_page = self.paginate_queryset(pets, request, view=self)
        serializer = PetSerializer(result_page, many=True)

        return self.get_paginated_response(serializer.data)


class PetParamView(APIView):
    def get(sef, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(pet)

        return Response(serializer.data, 200)

    def patch(sef, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        serializer = PetSerializer(data=request.data, partial=True)

        serializer.is_valid(raise_exception=True)

        group_data = serializer.validated_data.pop("group", None)

        traits_data = serializer.validated_data.pop("traits", None)

        if group_data:
            try:
                group = Group.objects.get(scientific_name=group_data["scientific_name"])
            except Group.DoesNotExist:
                group = Group.objects.create(**group_data)
            serializer.validated_data["group"] = group

        if traits_data:
            list_traits = []

            for trait in traits_data:
                trait_obj = Trait.objects.filter(name__iexact=trait["name"]).first()

                if not trait_obj:
                    trait_obj = Trait.objects.create(**trait)

                list_traits.append(trait_obj)
            pet.traits.set(list_traits)

        for key, value in serializer.validated_data.items():
            setattr(pet, key, value)

        pet.save()

        serializer = PetSerializer(pet)

        return Response(serializer.data, 200)

    def delete(sef, request, pet_id):
        pet = get_object_or_404(Pet, id=pet_id)
        pet.delete()

        return Response(status=204)
