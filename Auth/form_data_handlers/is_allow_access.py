def is_allow_access(ctx: any, params: dict) -> bool:
    # 'submit_allow_access' in params and
    return  params == {} and ('grant_access' in ctx.response.url or 'access_token' in ctx.response.url)