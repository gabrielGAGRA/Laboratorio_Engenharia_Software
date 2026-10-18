"""User profile, subscription plans, premium, and family plan router."""

from typing import Annotated

from fastapi import APIRouter, Depends, Query

from app.application.commands import UpdateProfileCommand
from app.application.use_cases.user import (
    AddFamilyMemberUseCase,
    CancelSubscriptionPlanUseCase,
    ChangeSubscriptionPlanUseCase,
    ChangeTrackInteractionUseCase,
    DeleteUserAccountUseCase,
    GetAnnualListeningStatsUseCase,
    GetUserProfileUseCase,
    LinkSpotifyAccountUseCase,
    ListBlockedGenresUseCase,
    ListFamilyMembersUseCase,
    ListPlansUseCase,
    ListUserInteractionsUseCase,
    RemoveFamilyMemberUseCase,
    UpdateBlockedGenresUseCase,
    UpdateProfileUseCase,
)
from app.domain.models.interaction import InteractionAction
from app.presentation.dependencies import (
    get_add_family_member_use_case,
    get_annual_stats_use_case,
    get_cancel_subscription_plan_use_case,
    get_change_subscription_plan_use_case,
    get_change_track_interaction_use_case,
    get_delete_user_account_use_case,
    get_link_spotify_account_use_case,
    get_list_blocked_genres_use_case,
    get_list_family_members_use_case,
    get_list_plans_use_case,
    get_list_user_interactions_use_case,
    get_remove_family_member_use_case,
    get_update_blocked_genres_use_case,
    get_update_profile_use_case,
    get_user_profile_use_case,
    require_user,
)
from app.presentation.schemas import (
    ActionSuccessResponse,
    AddFamilyMemberRequest,
    AnnualStatsResponse,
    BlockedGenresRequest,
    ChangeInteractionRequest,
    ChangePlanRequest,
    InteractionResponse,
    LinkSpotifyRequest,
    PlanResponse,
    UpdateProfileRequest,
    UserProfileResponse,
    UserResponse,
)

router = APIRouter(tags=["Profile & Plans"])


@router.get("/api/profile/me", response_model=UserProfileResponse)
def get_profile(
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[GetUserProfileUseCase, Depends(get_user_profile_use_case)],
) -> UserProfileResponse:
    data = use_case.execute(user_id=user_id)
    return UserProfileResponse.model_validate(data)


@router.put("/api/profile/me", response_model=UserResponse)
def update_profile(
    req: UpdateProfileRequest,
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[UpdateProfileUseCase, Depends(get_update_profile_use_case)],
) -> UserResponse:
    user = use_case.execute(
        UpdateProfileCommand(
            user_id=user_id,
            display_name=req.display_name,
            new_password=req.new_password,
            current_password=req.current_password,
        )
    )
    return UserResponse.model_validate(user)


@router.post("/api/profile/link-spotify", response_model=UserResponse)
def link_spotify(
    req: LinkSpotifyRequest,
    use_case: Annotated[
        LinkSpotifyAccountUseCase, Depends(get_link_spotify_account_use_case)
    ],
) -> UserResponse:
    user = use_case.execute(
        user_id=req.user_id,
        spotify_id=req.spotify_id,
    )
    return UserResponse.model_validate(user)


@router.get("/api/plans", response_model=list[PlanResponse])
def list_plans(
    use_case: Annotated[ListPlansUseCase, Depends(get_list_plans_use_case)],
) -> list[PlanResponse]:
    plans = use_case.execute()
    return [PlanResponse.model_validate(p) for p in plans]


@router.post("/api/profile/plan", response_model=UserResponse)
def change_plan(
    req: ChangePlanRequest,
    use_case: Annotated[
        ChangeSubscriptionPlanUseCase,
        Depends(get_change_subscription_plan_use_case),
    ],
) -> UserResponse:
    user = use_case.execute(
        user_id=req.user_id,
        new_plan_id=req.new_plan_id,
    )
    return UserResponse.model_validate(user)


@router.delete("/api/profile/plan", response_model=UserResponse)
def cancel_plan(
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[
        CancelSubscriptionPlanUseCase,
        Depends(get_cancel_subscription_plan_use_case),
    ],
) -> UserResponse:
    user = use_case.execute(user_id=user_id)
    return UserResponse.model_validate(user)


@router.delete("/api/profile/account", response_model=ActionSuccessResponse)
def delete_account(
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[
        DeleteUserAccountUseCase, Depends(get_delete_user_account_use_case)
    ],
) -> ActionSuccessResponse:
    success = use_case.execute(user_id=user_id)
    return ActionSuccessResponse(success=success)


# --- Premium Routes ---


@router.get("/api/profile/stats", response_model=AnnualStatsResponse)
def get_annual_stats(
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[
        GetAnnualListeningStatsUseCase, Depends(get_annual_stats_use_case)
    ],
) -> AnnualStatsResponse:
    stats = use_case.execute(user_id=user_id)
    return AnnualStatsResponse.model_validate(stats)


@router.put("/api/profile/interaction", response_model=InteractionResponse)
def change_interaction(
    req: ChangeInteractionRequest,
    use_case: Annotated[
        ChangeTrackInteractionUseCase,
        Depends(get_change_track_interaction_use_case),
    ],
) -> InteractionResponse:
    action = InteractionAction(req.new_action.lower())
    interaction = use_case.execute(
        user_id=req.user_id,
        track_id=req.track_id,
        new_action=action,
    )
    return InteractionResponse.model_validate(interaction)


@router.get("/api/profile/history", response_model=list[InteractionResponse])
def list_history(
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[
        ListUserInteractionsUseCase, Depends(get_list_user_interactions_use_case)
    ],
    category: Annotated[str | None, Query()] = None,
) -> list[InteractionResponse]:
    action = InteractionAction(category.lower()) if category else None
    items = use_case.execute(user_id=user_id, action=action)
    return [InteractionResponse.model_validate(i) for i in items]


@router.get("/api/profile/blocked-genres", response_model=list[str])
def list_blocked_genres(
    user_id: Annotated[int, Depends(require_user)],
    use_case: Annotated[
        ListBlockedGenresUseCase, Depends(get_list_blocked_genres_use_case)
    ],
) -> list[str]:
    return use_case.execute(user_id=user_id)


@router.put("/api/profile/blocked-genres", response_model=UserResponse)
def update_blocked_genres(
    req: BlockedGenresRequest,
    use_case: Annotated[
        UpdateBlockedGenresUseCase, Depends(get_update_blocked_genres_use_case)
    ],
) -> UserResponse:
    if isinstance(req.blocked_genres, str):
        blocked_list = [g.strip() for g in req.blocked_genres.split(",") if g.strip()]
    else:
        blocked_list = [str(g).strip() for g in req.blocked_genres if str(g).strip()]

    user = use_case.execute(
        user_id=req.user_id,
        blocked_genres=blocked_list,
    )
    return UserResponse.model_validate(user)


# --- Family Plan Routes ---


@router.get("/api/profile/family/members", response_model=list[UserResponse])
def list_family_members(
    primary_account_id: Annotated[int, Query()],
    use_case: Annotated[
        ListFamilyMembersUseCase, Depends(get_list_family_members_use_case)
    ],
) -> list[UserResponse]:
    members = use_case.execute(primary_user_id=primary_account_id)
    return [UserResponse.model_validate(m) for m in members]


@router.post("/api/profile/family/members", response_model=UserResponse)
def add_family_member(
    req: AddFamilyMemberRequest,
    use_case: Annotated[
        AddFamilyMemberUseCase, Depends(get_add_family_member_use_case)
    ],
) -> UserResponse:
    dependent = use_case.execute(
        primary_user_id=req.primary_account_id,
        dependent_user_id=req.dependent_user_id,
    )
    return UserResponse.model_validate(dependent)


@router.delete("/api/profile/family/members/{member_id}", response_model=UserResponse)
def remove_family_member(
    member_id: int,
    primary_account_id: Annotated[int, Query()],
    use_case: Annotated[
        RemoveFamilyMemberUseCase, Depends(get_remove_family_member_use_case)
    ],
) -> UserResponse:
    unlinked = use_case.execute(
        primary_user_id=primary_account_id,
        member_user_id=member_id,
    )
    return UserResponse.model_validate(unlinked)


__all__ = ["router"]
