from pyramid.security import Everyone, Authenticated

class AuthenticationPolicy(object):

    def unauthenticated_userid(self, request):
        return None

    def authenticated_userid(self, request):
        if request.operator:
            return request.operator.call
        else:
            return None


    def effective_principals(self, request):
        principals = [Everyone]
        if request.operator:
            principals += [Authenticated]
            for r in request.operator.Roles:
                principals += [r.role]
            #principals.extend(request.User.groups())
        return principals


class AuthorizationPolicy(object):

    def permits(self, context, principals, permission):
        if permission in principals and Authenticated in principals:
            return True
        return False


    def principals_allowed_by_permission(self, context, permission):
        raise NotImplementedError

