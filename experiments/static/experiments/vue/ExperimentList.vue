<template>
  <FancyList
      :items="items"
      :filter-definitions="filterDefinitions"
      :context="context"
      :searchable-fields="searchableFields"
      :num-item-options="numItemsOptions"
      :sort-definitions="sortDefinitions"
      :show-controls="showControls"
      :default-items-per-page="defaultItemsPerPage"
      :loaded="loaded"
  >
    <template #title="{ item: experiment, context }">
      <h4 v-html="experiment.title">
      </h4>
    </template>


    <template #actions="{ item: experiment, context }">
      <a
          :href="$url('experiments:detail', [experiment.pk])"
          class="icon-details pl-1"
          :title="$t('details')"
      >
      </a>
      <a
          :href="$url('experiments:edit',[experiment.pk])"
          class="icon-edit"
          :title="$t('edit')"
      >
      </a>
      <a
          :href="$url('experiments:delete_experiment', [experiment.pk])"
          class="icon-delete"
          :title="$t('delete')"
      >
      </a>
    </template>


    <template #undertitle="{ item: experiment, context }">
      <div class="ufl-undertitle-line">
        {{ $t('state') }}: {{ experiment.get_state_display }}
      </div>
      <div class="ufl-undertitle-line">
        {{ $t('num_datapoints') }}: {{ experiment.num_datapoints }}
      </div>
    </template>


    <template #details="{ item: experiment, context }">
      <div class="row">
        <div class="col-12 col-md-8">

          <table>
            <tbody>
              <tr>
                <td>
                  {{ $t('date_created') }}:
                </td>
                <td>
                  {{ experiment.date_created | date('YYYY-MM-DD') }}
                </td>
              </tr>
              <tr v-if="experiment.approved">
                <td>
                  {{ $t('access_key') }}:
                </td>
                <td>
                  {{ experiment.access_id }}
                </td>
              </tr>
              <tr>
                <td>
                  {{ $t('state') }}:
                </td>
                <td>
                  {{ experiment.get_state_display }}
                </td>
              </tr>
              <tr v-if="experiment.approved">
                <td>
                  {{ $t('webexp_location') }}:
                </td>
                <td>
                  <a :href="'https://' + context.webexp_host + '/' + experiment.folder_name + '/'"
                     target="_blank">
                    {{ context.webexp_host }}/{{ experiment.folder_name }}/
                  </a>
                </td>
              </tr>
              <tr  v-if="experiment.approved">
                <td>
                  {{ $t('webdav_location') }}:
                </td>
                <td>
                  {{ context.webexp_webdav_host }}/{{ experiment.folder_name }}/ -
                  <a :href="$url('main:help') +'#collapse-webdav'">
                    Help
                  </a>
                </td>
              </tr>
            </tbody>
          </table>

        </div>

        <div class="col-12 col-md-4">
          <table>
            <tbody>
              <tr v-if="experiment.approved">
                <td>
                  {{ $t('num_datapoints') }}:
                </td>
                <td class="ml-1">
                  {{ experiment.num_datapoints }}
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <a
                      :href="$url('experiments:edit',[experiment.pk])"
                      :title="$t('edit')"
                  >
                    {{ $t('edit') }}
                  </a>
                </td>
              </tr>
              <tr>
                <td colspan="2">
                  <a
                      :href="$url('experiments:detail', [experiment.pk])"
                      :title="$t('details')"
                  >
                    {{ $t('details') }}
                  </a>
                </td>
              </tr>
              <tr v-if="experiment.approved">
                <td colspan="2">
                  <a :href="$url('experiments:download', [experiment.pk, 'raw'])"
                     target="_blank">
                    {{ $t('download_raw') }}
                  </a>
                </td>
              </tr>
              <tr v-if="experiment.approved">
                <td colspan="2">
                  <a :href="$url('experiments:download', [experiment.pk, 'csv'])"
                     target="_blank">
                    {{ $t('download_csv') }}
                  </a>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>
    </template>
  </FancyList>
</template>

<script>
// Marks FancyList as a dependency. Your IDE won't find it, but Django will.
import FancyList from '';

export default {
  name: 'ExperimentList',
  components: {
    // Loaded by the load_vue_component tag, no need to manually load this
    FancyList
  },
  i18n: {
    messages: {
      en: {
        state: "Status",
        num_datapoints: "Data uploaded",
        access_key: "Access key",
        download_raw: "Download raw data",
        download_csv: "Download data as CSV",
        webexp_location: "Location",
        webdav_location: "WebDav Share",
        details: "More details",
        delete: "Delete experiment",
        edit: "Edit experiment",
        date_created: "Created on"
      },
      nl: {
        state: "Status",
        num_datapoints: "Ge-uploade data",
        access_key: "Access key",
        download_raw: "Download ruwe data",
        download_csv: "Download data als CSV",
        webexp_location: "Locatie",
        webdav_location: "WebDav Share",
        details: "Meer details",
        delete: "Verwijder experiment",
        edit: "Wijzig experiment",
        date_created: "Aangemaakt op",
      }
    }
  },
  data: function () {
    return {
      // Actual data loaded through $ufl_load in mounted()
      'items': [],
      'context': {},
      'searchableFields': [],
      'filterDefinitions': {},
      'numItemsOptions': [],
      'sortDefinitions': {},
      'showControls': false,
      'defaultItemsPerPage': 10,
      'loaded': false,
    };
  },
  mounted() {
    this.$ufl_load(this, this.$url('experiments:home_api', []));
  },
}
</script>

<style>
.ufl-details table {
  border-spacing: 5px 0;
}
.icon-details:before {
  content: "\E92F";
}

.icon-edit:before {
  content: "\E905";
}

.icon-delete:before {
  content: "\E9AC";
  color: #C00A35;
}
</style>