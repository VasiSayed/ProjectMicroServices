from rest_framework import serializers
from django.db.models import Q
from django.db import models
from .models import (
    Project, Purpose, Phase, Stage, Building, Level,
    Zone, Flattype, Flat,Subzone,Rooms,
    Category, CategoryLevel1, CategoryLevel2, CategoryLevel3,
    CategoryLevel4, CategoryLevel5, CategoryLevel6,TransferRule
)

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import requests

ORGANIZATION_SERVICE_URL = "http://127.0.0.1:8002/api/organizations/"
COMPANY_SERVICE_URL = "http://127.0.0.1:8002/api/companies/"
ENTITY_SERVICE_URL = "http://127.0.0.1:8002/api/entities/"
USER_SERVICE_URL = "http://127.0.0.1:8000/api/users/"

class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'

    def validate(self, data):
        token = self.context.get('auth_token') 
        headers = {}
        if token:
            headers["Authorization"] = f"Bearer {token}"

        org_id = data.get('organization_id')
        comp_id = data.get('company_id')
        ent_id = data.get('entity_id')
        created_by = data.get('created_by')

        # Exactly one of org/company/entity must be set
        ids = [bool(org_id), bool(comp_id), bool(ent_id)]
        if sum(ids) < 1:
            raise serializers.ValidationError("Atleast one of organization_id, company_id, or entity_id must be set.")

        if org_id:
            url = f"{ORGANIZATION_SERVICE_URL}{org_id}/"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                raise serializers.ValidationError({"organization_id": "Organization does not exist."})

        if comp_id:
            url = f"{COMPANY_SERVICE_URL}{comp_id}/"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                raise serializers.ValidationError({"company_id": "Company does not exist."})

        if ent_id:
            url = f"{ENTITY_SERVICE_URL}{ent_id}/"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                raise serializers.ValidationError({"entity_id": "Entity does not exist."})

        if created_by:
            url = f"{USER_SERVICE_URL}{created_by}/"
            resp = requests.get(url, headers=headers)
            if resp.status_code != 200:
                raise serializers.ValidationError({"created_by": "User does not exist."})
        return data
    

class PurposeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Purpose
        fields = ['id', 'project', 'name', 'is_active']


class PhaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Phase
        fields = ['id', 'project', 'purpose', 'name', 'is_active']


class StageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Stage
        fields = ['id','project','purpose', 'phase', 'name', 'sequence', 'is_active']


class SubzoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subzone
        fields = ['id', 'zone', 'name']





class BuildingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Building
        fields = ['id', 'name', 'project']

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ['id', 'name', 'building']




class FlattypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flattype
        fields = ['id', 'project', 'rooms', 'type_name']


class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ['id', 'building', 'level', 'Flattype', 'number']



# serializers.py

class FlatTypeMiniSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flattype
        fields = ['id', 'type_name']

class FlatMiniSerializer(serializers.ModelSerializer):
    flattype = FlatTypeMiniSerializer(read_only=True)

    class Meta:
        model = Flat
        fields = ['id', 'number', 'flattype']

class LevelWithFlatsSerializer(serializers.ModelSerializer):
    flats = serializers.SerializerMethodField()

    class Meta:
        model = Level
        fields = ['id', 'name', 'flats']

    def get_flats(self, obj):
        flats = obj.flat_set.select_related('flattype').all()
        return FlatMiniSerializer(flats, many=True).data





class PhaseListByProject(APIView):
    def get(self, request, project_id):
        try:
            phases = Phase.objects.filter(project_id=project_id)
            serializer = PhaseSerializer(phases, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except Project.DoesNotExist:
            return Response({"detail": "Project not found."}, status=status.HTTP_404_NOT_FOUND)
        
class BuildingWithLevelsSerializer(serializers.ModelSerializer):
    levels = LevelSerializer(many=True, source='level_set', read_only=True)
    
    class Meta:
        model = Building
        fields = ['id', 'name', 'levels']


class ZoneWithSubzonesSerializer(serializers.ModelSerializer):
    subzones = SubzoneSerializer(many=True, source='subzones', read_only=True)
    class Meta:
        model = Zone
        fields = ['id', 'building', 'level', 'name', 'subzones']


class LevelWithZonesSerializer(serializers.ModelSerializer):
    zones = ZoneWithSubzonesSerializer(many=True, source='zone_set', read_only=True)
    class Meta:
        model = Level
        fields = ['id', 'name', 'zones']

class BuildingWithLevelsAndZonesSerializer(serializers.ModelSerializer):
    levels = LevelWithZonesSerializer(many=True, source='level_set', read_only=True)
    class Meta:
        model = Building
        fields = ['id', 'name', 'levels']


class BuildingWithLevelsZonesCreateSerializer(serializers.ModelSerializer):
    levels = LevelSerializer(many=True, required=False)

    class Meta:
        model = Building
        fields = ['id', 'name', 'project', 'levels']

    def create(self, validated_data):
        levels_data = validated_data.pop('levels', [])
        building = Building.objects.create(**validated_data)
        for level_data in levels_data:
            zones_data = level_data.pop('zones', [])
            level = Level.objects.create(building=building, **level_data)
            for zone_data in zones_data:
                subzones_data = zone_data.pop('subzones', [])
                zone = Zone.objects.create(building=building, level=level, **zone_data)
                for subzone_data in subzones_data:
                    Subzone.objects.create(zone=zone, **subzone_data)
        return building


class SubzoneCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Subzone
        fields = ["name"]

class ZoneCreateSerializer(serializers.ModelSerializer):
    subzones = SubzoneCreateSerializer(many=True, required=False)

    class Meta:
        model = Zone
        fields = ["name", "subzones"]

class LevelZoneBulkCreateSerializer(serializers.Serializer):
    level = serializers.PrimaryKeyRelatedField(queryset=Level.objects.all())
    zones = ZoneCreateSerializer(many=True)

    def create(self, validated_data):
        level = validated_data["level"]
        zones_data = validated_data.get("zones", [])
        created_zones = []
        for zone_data in zones_data:
            subzones_data = zone_data.pop("subzones", [])
            zone = Zone.objects.create(
                name=zone_data["name"],
                building=level.building,
                level=level,
            )
            for subzone_data in subzones_data:
                Subzone.objects.create(
                    name=subzone_data["name"],
                    zone=zone,
                )
            created_zones.append(zone)
        return {"level": level, "zones": created_zones}



class RoomSerializer(serializers.ModelSerializer):
    class Meta:
        model = Rooms
        fields = '__all__'


class CategorySimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name','project']

class CategoryLevel1SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel1
        fields = ['id', 'name', 'category', 'created_by']

class CategoryLevel2SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel2
        fields = ['id', 'name', 'category_level1', 'created_by']

class CategoryLevel3SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel3
        fields = ['id', 'name', 'category_level2', 'created_by']

class CategoryLevel4SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel4
        fields = ['id', 'name', 'category_level3', 'created_by']

class CategoryLevel5SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel5
        fields = ['id', 'name', 'category_level4', 'created_by']

class CategoryLevel6SimpleSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel6
        fields = ['id', 'name', 'category_level5', 'created_by']



class CategoryLevel6Serializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel6
        fields = ['id', 'name','category_level5','created_by']

class CategoryLevel5Serializer(serializers.ModelSerializer):
    level6 = CategoryLevel6Serializer(many=True, read_only=True)

    class Meta:
        model = CategoryLevel5
        fields = ['id', 'name', 'level6']

class CategoryLevel4Serializer(serializers.ModelSerializer):
    level5 = CategoryLevel5Serializer(many=True, read_only=True)

    class Meta:
        model = CategoryLevel4
        fields = ['id', 'name', 'level5']

class CategoryLevel3Serializer(serializers.ModelSerializer):
    level4 = CategoryLevel4Serializer(many=True, read_only=True)

    class Meta:
        model = CategoryLevel3
        fields = ['id', 'name', 'level4']

class CategoryLevel2Serializer(serializers.ModelSerializer):
    level3 = CategoryLevel3Serializer(many=True, read_only=True)

    class Meta:
        model = CategoryLevel2
        fields = ['id', 'name', 'level3']

class CategoryLevel1Serializer(serializers.ModelSerializer):
    level2 = CategoryLevel2Serializer(many=True, read_only=True)

    class Meta:
        model = CategoryLevel1
        fields = ['id', 'name', 'level2']

class CategorySerializer(serializers.ModelSerializer):
    level1 = CategoryLevel1Serializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ['id', 'name', 'level1']



class FlatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Flat
        fields = ['id', 'number', 'level', 'building', 'project','flattype']  

class ZoneWithFlatsSerializer(serializers.ModelSerializer):
    flats = serializers.SerializerMethodField()

    class Meta:
        model = Zone
        fields = ['id', 'name', 'level', 'building', 'flats']

    def get_flats(self, obj):
        # You may need to adjust this if you have a direct relation, otherwise filter by level/building/zone
        flats = Flat.objects.filter(level=obj.level, building=obj.building)
        return FlatSerializer(flats, many=True).data

class LevelWithZonesAndFlatsSerializer(serializers.ModelSerializer):
    zones = ZoneWithFlatsSerializer(many=True, source='zone_set', read_only=True)

    class Meta:
        model = Level
        fields = ['id', 'name', 'zones']

class BuildingWithAllDetailsSerializer(serializers.ModelSerializer):
    levels = LevelWithZonesAndFlatsSerializer(many=True, source='level_set', read_only=True)

    class Meta:
        model = Building
        fields = ['id', 'name', 'levels']




class TransferRuleSerializer(serializers.ModelSerializer):
    class Meta:
        model = TransferRule
        fields = ['id', 'project', 'flat_level', 'room_level', 'checklist_level', 'question_level']


class ZoneSerializer(serializers.ModelSerializer):
    class Meta:
        model = Zone
        fields = ['id', 'name']

class BuildingSerializer(serializers.ModelSerializer):
    zones = ZoneSerializer(many=True, source='zone_set', read_only=True)

    class Meta:
        model = Building
        fields = ['id', 'name','project', 'zones']

class ProjectSerializer(serializers.ModelSerializer):
    buildings = BuildingSerializer(many=True, source='building_set', read_only=True)
    class Meta:
        model = Project
        fields = [
            'id', 'name', 'organization_id', 'company_id', 'entity_id', 'image', 'created_by','buildings'
        ]


class CategoryLevel6TreeSerializer(serializers.ModelSerializer):
    class Meta:
        model = CategoryLevel6
        fields = ['id', 'name']

class CategoryLevel5TreeSerializer(serializers.ModelSerializer):
    level6 = CategoryLevel6TreeSerializer(many=True, read_only=True)
    class Meta:
        model = CategoryLevel5
        fields = ['id', 'name', 'level6']

class CategoryLevel4TreeSerializer(serializers.ModelSerializer):
    level5 = CategoryLevel5TreeSerializer(many=True, read_only=True)
    class Meta:
        model = CategoryLevel4
        fields = ['id', 'name', 'level5']

class CategoryLevel3TreeSerializer(serializers.ModelSerializer):
    level4 = CategoryLevel4TreeSerializer(many=True, read_only=True)
    class Meta:
        model = CategoryLevel3
        fields = ['id', 'name', 'level4']

class CategoryLevel2TreeSerializer(serializers.ModelSerializer):
    level3 = CategoryLevel3TreeSerializer(many=True,  read_only=True)
    class Meta:
        model = CategoryLevel2
        fields = ['id', 'name', 'level3']

class CategoryLevel1TreeSerializer(serializers.ModelSerializer):
    level2 = CategoryLevel2TreeSerializer(many=True, read_only=True)
    class Meta:
        model = CategoryLevel1
        fields = ['id', 'name', 'level2']

class CategoryTreeSerializer(serializers.ModelSerializer):
    level1 = CategoryLevel1TreeSerializer(many=True,  read_only=True)
    class Meta:
        model = Category
        fields = ['id', 'name', 'level1']
