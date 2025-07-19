import { createRouter, createWebHistory, RouteRecordRaw } from "vue-router";
import { authGuard, permissionGuard } from './guards';

import ErrorPage from "@/modules/ErrorPage.vue";
import Forbidden from "@/modules/Forbidden.vue";
import EntityIndex from "../modules/entities/views/EntityIndex.vue"
import EntitieDetails from "@/modules/entities/views/EntitieDetails.vue";
import Dashboard from "@/modules/dashboard/views/Dashboard.vue";
import PointFocaux from "@/modules/entities/views/EntityFocalPoint.vue";
import Logs from "@/modules/logs/views/Logs.vue";
import VendorList from "@/modules/vendor/views/vendorList.vue";
import History from "@/modules/history/views/History.vue";
import Users from "@/modules/users/views/Users.vue";
import AddUser from "@/modules/users/views/AddUser.vue";""
import Scans from "@/modules/scans/views/Scans.vue";
import DefacementList from "@/modules/defacement/views/DefacementList.vue";
import EmailAlert from "@/modules/email/views/EmailAlert.vue";
import focalfunctions from "@/modules/focalPoints/focalfunctions.vue";
import FocalPoints from "@/modules/focalPoints/focalPoints.vue";
import mail_settings from "@/modules/mail_settings/views/mail_settings.vue";
import settings from "@/modules/general_settings/views/settings.vue";
import tools_integrated from "@/modules/integrations/views/tools_integrated.vue";
import roles from "@/modules/role/views/roles.vue";
import rolesedit from "@/modules/role/views/rolesedit.vue";
import account_settings from "@/modules/settings/views/account_settings.vue";
import change_password from "@/modules/settings/views/change_password.vue";
import DefacementsDetails from "@/modules/defacement/views/DefacementsDetails.vue";
import LoginPage from "@/modules/auth/LoginPage.vue";
import RegisterPage from "@/modules/auth/RegisterPage.vue";
import ForgetPasswordPage from "@/modules/auth/ForgetPasswordPage.vue";
import ConfirmMailPage from "@/modules/auth/ConfirmMailPage.vue";
import ResetPasswordPage from "@/modules/auth/ResetPasswordPage.vue";
import Logout from "@/modules/auth/Logout.vue";
import carousel from "@/modules/carousel/carousel.vue";

const routes: Array<RouteRecordRaw> = [
  {
    path: "/defacements/details/:id",
    name: "defacementsDetails", 
    component: DefacementsDetails,
    meta: {
      requiresAuth: true,
      permissions: ['defacement_view', 'entities_view']
    }
  },
  {
    path: "/dashboard/carousel",
    name: "carousel", 
    component: carousel,
    meta: {
      requiresAuth: true,
      permissions: ['dashboard_carousel_view', 'platforms_view']
    }
  },
  {
    path: "/settings/myaccount-settings",
    name: "accounSettings", 
    component: account_settings,
    meta: {
      requiresAuth: true,
    }
  },
  {
    path: "/settings/change-mypassword",
    name: "changePassword", 
    component: change_password,
    meta: {
      requiresAuth: true,
    }
  },
  {
    path: "/config/roles-create",
    name: "rolescreate", 
    component: rolesedit,
    meta: {
      requiresAuth: true,
      permissions: ['roles_create']
    }
  },
  {
    path: "/config/roles-edit/:id",
    name: "rolesedit", 
    component: rolesedit,
    meta: {
      requiresAuth: true,
      permissions: ['roles_view']
    }
  },
  {
    path: "/config/roles",
    name: "roles", 
    component: roles,
    meta: {
      requiresAuth: true,
      permissions: ['roles_view']
    }
  },
  {
    path: "/config/integrations",
    name: "integrations", 
    component: tools_integrated,
    meta: {
      requiresAuth: true,
      permissions: ['integrations_view']
    }
  },
  {
    path: "/config/general-settings",
    name: "general_settings", 
    component: settings,
    meta: {
      requiresAuth: true,
      permissions: ['config_view']
    }
  },
  {
    path: "/config/mail-settings",
    name: "mail_settings", 
    component: mail_settings,
    meta: {
      requiresAuth: true,
      permissions: ['mail_settings_view']
    }
  },
  {
    path: "/focal/functions",
    name: "focalFunctions", 
    component: focalfunctions,
    meta: {
      requiresAuth: true,
      permissions: ['focal_functions_view']
    }
  },
  {
    path: "/focal/points",
    name: "focalPoint", 
    component: FocalPoints,
    meta: {
      requiresAuth: true,
      permissions: ['focal_points_view']
    }
  },
  {
    path: "/focal/points/:id",
    name: "focalPoints", 
    component: FocalPoints,
    meta: {
      requiresAuth: true,
      permissions: ['focal_functions_view']
    }
  },
  {
    path: "/emailing/:id",
    name: 'emailing',
    component: EmailAlert,
    meta: {
      requiresAuth: true,
      permissions: ['focal_points_view', 'alerts_view']
    }
  },
  {
    path: "/defacements/list",
    name: "DefacementList", 
    component: DefacementList,
    meta: {
      requiresAuth: true,
      permissions: ['defacement_view', 'entities_view']
    }
  },
  {
    path: "/scans",
    name: "Scans", 
    component: Scans,
    meta: {
      requiresAuth: true,
      permissions: ['cerb_scans_view']
    }
  },
  {
    path: "/users/edit/:id",
    name: "EditUser", 
    component: AddUser,
    meta: {
      requiresAuth: true,
      permissions: ['users_edit']
    }
  },
  {
    path: "/users/add",
    name: "AddUser", 
    component: AddUser,
    meta: {
      requiresAuth: true,
      permissions: ['users_create']
    }
  },
  {
    path: "/users",
    name: "Users", 
    component: Users,
    meta: {
      requiresAuth: true,
      permissions: ['users_view']
    }
  },
  {
    path: "/history",
    name: "History", 
    component: History,
    meta: {
      requiresAuth: true,
      permissions: ['alerts_view', 'entities_view']
    }
  },
  {
    path: "/vendor",
    name: "VendorList", 
    component: VendorList,
    meta: {
      requiresAuth: true,
      permissions: ['vendor_list_view']
    }
  },

  {
    path: "/logs",
    name: "Logs",
    component: Logs,
    meta: {
      requiresAuth: true,
      permissions: ['logs_view']
    }
  },
  {
    path: "/entities/focalpoints/:id",
    name: "PointFocaux",
    component: PointFocaux,
    meta: {
      requiresAuth: true,
      permissions: ['focal_points_view']
    }
  },
  {
    path: "/entities",
    name: "EntitieList",
    component: EntityIndex,
    meta: {
      requiresAuth: true,
      permissions: ['entities_view']
    }
  },
  {
    path: "/entitie/details/:id",
    name: "EntitieDetails",
    component: EntitieDetails,
    meta: {
      requiresAuth: true,
      permissions: ['entities_view']
    }
  },
  {
    path: "/dashboard",
    name: "Dashboard",
    component: Dashboard,
    meta: {
      requiresAuth: true,
    }
  },
  {
    path: "/403",
    name: "forbidden",
    component: Forbidden
  },
  {
    path: "/authentication/login",
    name: "LoginPage",
    component: LoginPage,
    meta: { guest: true }
  },
  {
    path: "/authentication/register",
    name: "RegisterPage",
    component: RegisterPage,
    meta: { guest: true }
  },
  {
    path: "/authentication/reset-password/:token",
    name: "ResetPasswordPage",
    component: ResetPasswordPage,
    meta: { guest: true }
  },
  {
    path: "/authentication/forget-password",
    name: "ForgetPasswordPage",
    component: ForgetPasswordPage,
    meta: { guest: true }
  },
  {
    path: "/authentication/logout",
    name: "LogOutPage",
    component: Logout,
    meta: { requiresAuth: true }
  },
  {
    path: '/',
    redirect: '/authentication/login' 
  },
  {
    path: "/authentication/confirm-mail",
    name: "ConfirmMailPage",
    component: ConfirmMailPage,
    meta: { guest: true }
  },

  { path: "/:pathMatch(.*)*", name: "ErrorPage", component: ErrorPage },
];

const router = createRouter({
  history: createWebHistory(),
  routes,
  linkExactActiveClass: "active",
  scrollBehavior() {
    return { top: 0, behavior: "smooth" };
  },
});

router.beforeEach(authGuard);

router.beforeEach((to, from, next) => {
  if (to.meta.permissions) {
    return permissionGuard(to.meta.permissions as string[])(to, from, next);
  }
  next();
});
router.beforeEach((to, from, next) => {
  if (to.matched.some(record => record.meta.requiresAuth)) {
    return authGuard(to, from, next);
  }
  next();
});

export default router;
