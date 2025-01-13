const routes = [
  {
    path: '/',
    component: () => import('layouts/MainLayout.vue'),
    children: [
      { path: '', component: () => import('pages/IndexPage.vue') },                 // Index page
      { path: 'login', component: () => import('pages/LoginPage.vue') },            // Login page
      { path: 'page-import', component: () => import('pages/tmpImportView.vue') } // tmpImportView
    ]
  },

  // Always leave this as last one,
  // but you can also remove it
  {
    path: '/:catchAll(.*)*',
    component: () => import('pages/ErrorNotFound.vue')
  },
]

export default routes
