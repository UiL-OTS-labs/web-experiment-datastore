from cdh.vue.components import VueComponent, Vue

Vue.add_component(VueComponent(
    'ExperimentList',
    location='experiments/vue/ExperimentList.vue',
    subcomponents=[],
    depends=['FancyList']
))
