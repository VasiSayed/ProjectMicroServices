from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework import status,generics
from rest_framework import viewsets, permissions
from rest_framework.permissions import IsAuthenticated

from .models import (
    Project, Purpose, Phase, Stage, Building, Level,
    Zone, Flattype, Flat,Subzone,Rooms,    Category, CategoryLevel1, CategoryLevel2, CategoryLevel3,
    CategoryLevel4, CategoryLevel5, CategoryLevel6,TransferRule
)
from .serializers import (
    ProjectSerializer, PurposeSerializer, PhaseSerializer,
    StageSerializer, BuildingSerializer, LevelSerializer,
    ZoneSerializer, FlattypeSerializer, FlatSerializer,BuildingWithLevelsSerializer,
    BuildingWithLevelsAndZonesSerializer,SubzoneSerializer,BuildingWithLevelsZonesCreateSerializer,
    LevelZoneBulkCreateSerializer,RoomSerializer,
    CategorySerializer, CategoryLevel1Serializer, CategoryLevel2Serializer, CategoryLevel3Serializer,
    CategoryLevel4Serializer, CategoryLevel5Serializer, CategoryLevel6Serializer
    ,BuildingWithAllDetailsSerializer,TransferRuleSerializer,CategorySimpleSerializer,
       CategoryLevel1SimpleSerializer, CategoryLevel2SimpleSerializer,
    CategoryLevel3SimpleSerializer, CategoryLevel4SimpleSerializer,
    CategoryLevel5SimpleSerializer, CategoryLevel6SimpleSerializer

)

from .serializers import CategoryTreeSerializer

class CategoryTreeByProjectAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        project_id = request.query_params.get('project')
        if not project_id:
            return Response({'detail': 'Missing project parameter'}, status=400)
        categories = Category.objects.filter(project_id=project_id)
        serializer = CategoryTreeSerializer(categories, many=True)
        print(serializer.data)
        return Response(serializer.data)
    
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Project
import requests

USER_SERVICE_URL = "http://192.168.1.28:8000"  # To fetch users if needed

class OrgProjectUserSummaryAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        org_ids = Project.objects.values_list('organization_id', flat=True).distinct()
        result = []

        for org_id in org_ids:
            org_data = {"org_id": org_id}
            projects = Project.objects.filter(organization_id=org_id)
            project_list = []
            user_ids = set()
            for project in projects:
                project_list.append({
                    "project_id": project.id,
                    "project_name": project.name,
                    "created_by": project.created_by
                })
                user_ids.add(project.created_by)
            users_data = []
            if user_ids:
                try:
                    resp = requests.get(
                        f"{USER_SERVICE_URL}/api/users/",
                        params={"ids": ','.join(map(str, user_ids))},
                        timeout=5
                    )
                    if resp.ok:
                        users_data = resp.json()
                except Exception:
                    pass

            org_data["projects"] = project_list
            org_data["project_count"] = len(project_list)
            org_data["user_ids"] = list(user_ids)
            org_data["users"] = users_data  

            result.append(org_data)
        return Response(result)

class CategorySimpleViewSet(viewsets.ModelViewSet):
    queryset = Category.objects.all()
    serializer_class = CategorySimpleSerializer


class CategoryLevel1SimpleViewSet(viewsets.ModelViewSet):
    queryset = CategoryLevel1.objects.all()
    serializer_class = CategoryLevel1SimpleSerializer

class CategoryLevel2SimpleViewSet(viewsets.ModelViewSet):
    queryset = CategoryLevel2.objects.all()
    serializer_class = CategoryLevel2SimpleSerializer

class CategoryLevel3SimpleViewSet(viewsets.ModelViewSet):
    queryset = CategoryLevel3.objects.all()
    serializer_class = CategoryLevel3SimpleSerializer

class CategoryLevel4SimpleViewSet(viewsets.ModelViewSet):
    queryset = CategoryLevel4.objects.all()
    serializer_class = CategoryLevel4SimpleSerializer

class CategoryLevel5SimpleViewSet(viewsets.ModelViewSet):
    queryset = CategoryLevel5.objects.all()
    serializer_class = CategoryLevel5SimpleSerializer

class CategoryLevel6SimpleViewSet(viewsets.ModelViewSet):
    queryset = CategoryLevel6.objects.all()
    serializer_class = CategoryLevel6SimpleSerializer

class BulkLevelZonesSubzonesCreateAPIView(APIView):
    def post(self, request):
        serializer = LevelZoneBulkCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Zones and subzones created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class ProjectViewSet(viewsets.ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


    def get_serializer_context(self):
        context = super().get_serializer_context()
        auth_header = self.request.headers.get('Authorization')
        token = None
        if auth_header and auth_header.startswith('Bearer '):
            token = auth_header.split(' ')[1]
        context['auth_token'] = token
        return context



class PurposeViewSet(viewsets.ModelViewSet):
    queryset = Purpose.objects.all()
    serializer_class = PurposeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


class PhaseViewSet(viewsets.ModelViewSet):
    queryset = Phase.objects.all()
    serializer_class = PhaseSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)
    
    @action(detail=False, methods=['get'], url_path='by-purpose/(?P<purpose_id>[^/.]+)')
    def by_purpose(self, request, purpose_id=None):
        phases = self.get_queryset().filter(purpose_id=purpose_id)
        serializer = self.get_serializer(phases, many=True)
        return Response(serializer.data)
    

class StageViewSet(viewsets.ModelViewSet):
    queryset = Stage.objects.all()
    serializer_class = StageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

class BuildingViewSet(viewsets.ModelViewSet):
    queryset = Building.objects.all()
    serializer_class = BuildingSerializer
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

class ZoneViewSet(viewsets.ModelViewSet):
    queryset = Zone.objects.all()
    serializer_class = ZoneSerializer
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

class FlattypeViewSet(viewsets.ModelViewSet):
    queryset = Flattype.objects.all()
    serializer_class = FlattypeSerializer
    permission_classes = [permissions.IsAuthenticated]
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)

class FlatViewSet(viewsets.ModelViewSet):
    queryset = Flat.objects.all()
    serializer_class = FlatSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)


class PurposeListByProject(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        purpose = Purpose.objects.filter(project__id=project_id)
        serializer = PurposeSerializer(purpose, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)



class PhaseListByProject(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        phases = Phase.objects.filter(project__id=project_id)
        serializer = PhaseSerializer(phases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class PhaseCreateView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        serializer = PhaseSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class StageListByProject(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, project_id):
        stage = Stage.objects.filter(phase__project__id=project_id)
        serializer = StageSerializer(stage, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PurposeListByProject(APIView):
    def get(self, request, project_id):
        purposes = Purpose.objects.filter(project_id=project_id)
        serializer = PurposeSerializer(purposes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

class PhaseListByProject(APIView):
    def get(self, request, project_id):
        phases = Phase.objects.filter(project_id=project_id)
        serializer = PhaseSerializer(phases, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Stages by Phase
class StageListByPhase(APIView):
    def get(self, request, phase_id):
        stages = Stage.objects.filter(phase_id=phase_id)
        serializer = StageSerializer(stages, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Buildings by Project
class BuildingListByProject(APIView):
    def get(self, request, project_id):
        # print(project_id,'projectiddd')
        buildings = Building.objects.filter(project_id=project_id)
        serializer = BuildingSerializer(buildings, many=True)
        # print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)


# Levels by Building
class LevelListByBuilding(APIView):
    def get(self, request, building_id):
        levels = Level.objects.filter(building_id=building_id)
        serializer = LevelSerializer(levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Zones by Building
class ZoneListByBuilding(APIView):
    def get(self, request, building_id):
        zones = Zone.objects.filter(building_id=building_id)
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Zones by Level
class ZoneListByLevel(APIView):
    def get(self, request, level_id):
        zones = Zone.objects.filter(level_id=level_id)
        serializer = ZoneSerializer(zones, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Flattype by Project
class FlattypeListByProject(APIView):
    def get(self, request, project_id):
        flattypes = Flattype.objects.filter(project_id=project_id)
        serializer = FlattypeSerializer(flattypes, many=True)
        print(serializer.data)
        return Response(serializer.data, status=status.HTTP_200_OK)

class FLatssbyProjectId(APIView):
    def get(self,request,project_id):
        flats=Flat.objects.filter(project=project_id)
        serizlizer=FlatSerializer(flats,many=True)
        print(serizlizer.data)
        return Response(serizlizer.data,status=status.HTTP_200_OK)

# Flat by Building
class FlatListByBuilding(APIView):
    def get(self, request, building_id):
        flats = Flat.objects.filter(building_id=building_id)
        serializer = FlatSerializer(flats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Flat by Level
class FlatListByLevel(APIView):
    def get(self, request, level_id):
        flats = Flat.objects.filter(level_id=level_id)
        serializer = FlatSerializer(flats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

# Flat by Flattype
class FlatListByFlattype(APIView):
    def get(self, request, flattype_id):
        flats = Flat.objects.filter(flattype_id=flattype_id)
        serializer = FlatSerializer(flats, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

# class GetProjectsByUser(APIView):
#     def get(self, request):
#         user_id = request.GET.get('user_id')
#         if not user_id:
#             return Response({"error": "user_id is required"}, status=status.HTTP_400_BAD_REQUEST)
        
#         projects = Project.objects.filter(created_by=user_id)
#         serializer = ProjectSerializer(projects, many=True)
#         print(serializer.data)
#         return Response(serializer.data, status=status.HTTP_200_OK)
    
class GetProjectsByUser(APIView):
    permission_classes = [IsAuthenticated]  

    def get(self, request):
        user = request.user 
        projects = Project.objects.filter(created_by=user.id) 
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    

class BuildingWithLevelsByProject(APIView):
    def get(self, request, project_id):
        buildings = Building.objects.filter(project_id=project_id)
        serializer = BuildingWithLevelsSerializer(buildings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class BuildingsWithLevelsAndZonesByProject(APIView):
    def get(self, request, project_id):
        buildings = Building.objects.filter(project_id=project_id)
        serializer = BuildingWithLevelsAndZonesSerializer(buildings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class NestedBuildingCreateView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = BuildingWithLevelsAndZonesSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save() 
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SubzoneViewSet(viewsets.ModelViewSet):
    queryset = Subzone.objects.all()
    serializer_class = SubzoneSerializer

    @action(detail=True, methods=['get'])
    def subzones(self, request, pk=None):
        subzones = Subzone.objects.filter(zone_id=pk)
        serializer = SubzoneSerializer(subzones, many=True)
        return Response(serializer.data)




class BulkLevelZonesSubzonesCreateAPIView(APIView):
    def post(self, request):
        serializer = LevelZoneBulkCreateSerializer(data=request.data, many=True)
        if serializer.is_valid():
            serializer.save()
            return Response({"detail": "Zones and subzones created successfully."}, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Rooms.objects.all()
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        if not serializer.is_valid():
            print("Validation Errors:", serializer.errors)
            return Response(serializer.errors, status=400)
        self.perform_create(serializer)
        return Response(serializer.data, status=201)
    
    @action(detail=False, methods=['get'])
    def by_project(self, request):
        project_id = request.query_params.get('project_id')
        if not project_id:
            return Response({"error": "project_id is required."}, status=400)
        rooms = Rooms.objects.filter(Project_id=project_id)
        serializer = self.get_serializer(rooms, many=True)
        return Response(serializer.data)


class CreatedByMixin:
    def perform_create(self, serializer):
        serializer.save(created_by=self.request.user.id)

class CategoryViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategorySerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Category.objects.filter(created_by=self.request.user.id)

class CategoryLevel1ViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategoryLevel1Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryLevel1.objects.filter(created_by=self.request.user.id)
        category_id = self.request.query_params.get('category')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset

class CategoryLevel2ViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategoryLevel2Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryLevel2.objects.filter(created_by=self.request.user.id)
        level1_id = self.request.query_params.get('category_level1')
        if level1_id:
            queryset = queryset.filter(category_level1_id=level1_id)
        return queryset

class CategoryLevel3ViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategoryLevel3Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryLevel3.objects.filter(created_by=self.request.user.id)
        level2_id = self.request.query_params.get('category_level2')
        if level2_id:
            queryset = queryset.filter(category_level2_id=level2_id)
        return queryset

class CategoryLevel4ViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategoryLevel4Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryLevel4.objects.filter(created_by=self.request.user.id)
        level3_id = self.request.query_params.get('category_level3')
        if level3_id:
            queryset = queryset.filter(category_level3_id=level3_id)
        return queryset

class CategoryLevel5ViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategoryLevel5Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryLevel5.objects.filter(created_by=self.request.user.id)
        level4_id = self.request.query_params.get('category_level4')
        if level4_id:
            queryset = queryset.filter(category_level4_id=level4_id)
        return queryset

class CategoryLevel6ViewSet(CreatedByMixin, viewsets.ModelViewSet):
    serializer_class = CategoryLevel6Serializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = CategoryLevel6.objects.filter(created_by=self.request.user.id)
        level5_id = self.request.query_params.get('category_level5')
        if level5_id:
            queryset = queryset.filter(category_level5_id=level5_id)
        return queryset



# Fetch full category tree by project_id
class CategoriesByProjectView(APIView):
    def get(self, request, project_id):
        queryset = Category.objects.filter(project_id=project_id)
        serializer = CategorySerializer(queryset, many=True)
        return Response(serializer.data)
    
class BuildingToFlatsByProject(APIView):
    def get(self, request, project_id):
        buildings = Building.objects.filter(project_id=project_id)
        serializer = BuildingWithAllDetailsSerializer(buildings, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


from .serializers import LevelWithFlatsSerializer

class LevelsWithFlatsByBuilding(APIView):
    def get(self, request, building_id):
        levels = Level.objects.filter(building_id=building_id).order_by('-name')
        serializer = LevelWithFlatsSerializer(levels, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)


class TransferRuleViewSet(viewsets.ModelViewSet):
    queryset = TransferRule.objects.all()
    serializer_class = TransferRuleSerializer

    def get_queryset(self):
        project_id = self.request.query_params.get('project_id')
        if project_id:
            return self.queryset.filter(project__id=project_id)
        return self.queryset

    def create(self, request, *args, **kwargs):
        project_id = request.data.get("project_id") or request.data.get("project")
        if not project_id:
            return Response({"message": "Project ID is required"}, status=400)
        obj, created = TransferRule.objects.update_or_create(
            project_id=project_id,
            defaults={
                "flat_level": request.data.get("flat_level", False),
                "room_level": request.data.get("room_level", False),
                "checklist_level": request.data.get("checklist_level", False),
                "question_level": request.data.get("question_level", True),
            },
        )
        serializer = self.get_serializer(obj)
        return Response({"message": "Saved!", "data": serializer.data}, status=200)
    

class ProjectsByIdsAPIView(APIView):
    permission_classes = [permissions.IsAuthenticated]  # or AllowAny if public

    def post(self, request):
        ids = request.data.get("ids")
        if not ids or not isinstance(ids, list):
            return Response({"detail": "List of ids required as 'ids'"}, status=400)
        
        projects = Project.objects.filter(id__in=ids)
        data = ProjectSerializer(projects, many=True).data

        # Return as dict: {id: project_obj}
        result = {str(item['id']): item for item in data}
        return Response(result,status=200)


class ProjectsByOrganizationView(APIView):
    def get(self, request, organization_id):
        projects = Project.objects.filter(organization_id=organization_id)
        serializer = ProjectSerializer(projects, many=True)
        return Response(serializer.data)
    

class ProjectsByOwnershipParamView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        entity_id = request.query_params.get('entity_id')
        company_id = request.query_params.get('company_id')
        organization_id = request.query_params.get('organization_id')

        if entity_id:
            projects = Project.objects.filter(entity_id=entity_id)
        elif company_id:
            projects = Project.objects.filter(company_id=company_id)
        elif organization_id:
            projects = Project.objects.filter(organization_id=organization_id)
        else:
            projects = Project.objects.none()

        serializer = ProjectSerializer(projects, many=True)
        print(serializer.data)
        return Response(serializer.data)