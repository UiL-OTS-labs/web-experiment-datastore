from cdh.vue.components import VueComponent, Vue

Vue.add_component(VueComponent(
    'AdminExperimentList',
    location='administration/AdminExperimentList.vue',
    subcomponents=[],
    depends=['FancyList']
))
