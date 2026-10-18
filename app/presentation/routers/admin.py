"""Administration console router for catalog moderation and executive dashboard."""

from typing import TYPE_CHECKING, Annotated

from fastapi import APIRouter, Depends

from app.application.dtos.admin_dtos import UpdateSubscriptionPlanInput
from app.application.dtos.auth_dtos import AuthenticateUserInput
from app.presentation.dependencies import (
    get_audience_report_use_case,
    get_authenticate_admin_use_case,
    get_block_track_use_case,
    get_executive_dashboard_use_case,
    get_list_users_with_plans_use_case,
    get_promote_user_to_admin_use_case,
    get_top_moderation_reviews_use_case,
    get_update_subscription_plan_use_case,
    get_update_track_explicit_flag_use_case,
    require_admin,
)
from app.presentation.schemas import (
    AudienceReportResponse,
    ExecutiveDashboardResponse,
    LoginRequest,
    PlanResponse,
    ReviewResponse,
    TrackBlockResponse,
    TrackExplicitResponse,
    UpdatePlanAdminRequest,
    UpdateTrackExplicitRequest,
    UserPlanSummaryResponse,
    UserResponse,
)

if TYPE_CHECKING:
    from app.application.use_cases.admin import (
        BlockTrackUseCase,
        GetAudienceReportUseCase,
        GetExecutiveDashboardUseCase,
        GetTopModerationReviewsUseCase,
        ListUsersWithPlansUseCase,
        PromoteUserToAdminUseCase,
        UpdateSubscriptionPlanUseCase,
        UpdateTrackExplicitFlagUseCase,
    )
    from app.application.use_cases.auth import AuthenticateAdminUseCase

router = APIRouter(prefix="/api/admin", tags=["Admin Console"])


@router.post("/login", response_model=UserResponse)
def login_admin(
    req: LoginRequest,
    use_case: Annotated[
        AuthenticateAdminUseCase, Depends(get_authenticate_admin_use_case)
    ],
) -> UserResponse:
    admin = use_case.execute(
        AuthenticateUserInput(email=req.email, password=req.password)
    )
    return UserResponse.model_validate(admin)


@router.get(
    "/dashboard",
    response_model=ExecutiveDashboardResponse,
    dependencies=[Depends(require_admin)],
)
def get_executive_dashboard(
    use_case: Annotated[
        GetExecutiveDashboardUseCase, Depends(get_executive_dashboard_use_case)
    ],
) -> ExecutiveDashboardResponse:
    dashboard = use_case.execute()
    return ExecutiveDashboardResponse.model_validate(dashboard)


@router.get(
    "/users",
    response_model=list[UserPlanSummaryResponse],
    dependencies=[Depends(require_admin)],
)
def list_users(
    use_case: Annotated[
        ListUsersWithPlansUseCase, Depends(get_list_users_with_plans_use_case)
    ],
) -> list[UserPlanSummaryResponse]:
    users = use_case.execute()
    return [UserPlanSummaryResponse.model_validate(u) for u in users]


@router.get(
    "/audience",
    response_model=AudienceReportResponse,
    dependencies=[Depends(require_admin)],
)
def get_audience_report(
    use_case: Annotated[
        GetAudienceReportUseCase, Depends(get_audience_report_use_case)
    ],
) -> AudienceReportResponse:
    report = use_case.execute()
    return AudienceReportResponse.model_validate(report)


@router.post(
    "/tracks/{track_id}/block",
    response_model=TrackBlockResponse,
    dependencies=[Depends(require_admin)],
)
def block_track(
    track_id: int,
    use_case: Annotated[BlockTrackUseCase, Depends(get_block_track_use_case)],
) -> TrackBlockResponse:
    success = use_case.execute(track_id=track_id)
    return TrackBlockResponse(blocked=success)


@router.put(
    "/tracks/{track_id}/explicit",
    response_model=TrackExplicitResponse,
    dependencies=[Depends(require_admin)],
)
def update_track_explicit(
    track_id: int,
    req: UpdateTrackExplicitRequest,
    use_case: Annotated[
        UpdateTrackExplicitFlagUseCase,
        Depends(get_update_track_explicit_flag_use_case),
    ],
) -> TrackExplicitResponse:
    explicit = use_case.execute(
        track_id=track_id,
        explicit=req.explicit,
    )
    return TrackExplicitResponse(track_id=track_id, explicit=explicit)


@router.put(
    "/users/{user_id}/promote-admin",
    response_model=UserResponse,
    dependencies=[Depends(require_admin)],
)
def promote_user_to_admin(
    user_id: int,
    use_case: Annotated[
        PromoteUserToAdminUseCase, Depends(get_promote_user_to_admin_use_case)
    ],
) -> UserResponse:
    user = use_case.execute(user_id=user_id)
    return UserResponse.model_validate(user)


@router.put(
    "/plans/{plan_id}",
    response_model=PlanResponse,
    dependencies=[Depends(require_admin)],
)
def update_plan(
    plan_id: int,
    req: UpdatePlanAdminRequest,
    use_case: Annotated[
        UpdateSubscriptionPlanUseCase,
        Depends(get_update_subscription_plan_use_case),
    ],
) -> PlanResponse:
    input_dto = UpdateSubscriptionPlanInput(
        plan_id=plan_id,
        new_price=req.new_price,
        new_name=req.new_name,
        max_profiles=req.max_profiles,
    )
    plan = use_case.execute(input_dto)
    return PlanResponse.model_validate(plan)


@router.get(
    "/reviews",
    response_model=list[ReviewResponse],
    dependencies=[Depends(require_admin)],
)
def get_top_moderation_reviews(
    use_case: Annotated[
        GetTopModerationReviewsUseCase,
        Depends(get_top_moderation_reviews_use_case),
    ],
) -> list[ReviewResponse]:
    reviews = use_case.execute()
    return [ReviewResponse.model_validate(r) for r in reviews]
