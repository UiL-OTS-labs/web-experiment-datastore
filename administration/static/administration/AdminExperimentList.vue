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
          :href="$url('admin:experiments_experiment_change', [experiment.pk])"
          class="icon-edit pl-1"
          :title="$t('edit')"
      >
      </a>
      <a
          v-if="!experiment.approved"
          :href="$url('administration:approve', [experiment.pk])"
          class="icon-approve"
          :title="$t('approve')"
      >
      </a>
    </template>


    <template #undertitle="{ item: experiment, context }">
      <div class="ufl-undertitle-line">
        {{ $t('ID') }}: {{ experiment.pk }}
      </div>
      <div class="ufl-undertitle-line">
        {{ $t('state') }}: {{ experiment.get_state_display }}
      </div>
      <div class="ufl-undertitle-line">
        {{ $t('show_in_ldap_config') }}:
        {{ experiment.show_in_ldap_config ? $t('yes') : $t('no') }}
      </div>
    </template>


    <template #details="{ item: experiment, context }">
      <div class="row">
        <div class="col-12 col-md-8">
          <table>
            <tbody>
              <tr>
                <td>
                  {{ $t('ID') }}
                </td>
                <td>
                  {{ experiment.pk }}
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
              <tr>
                <td>
                  {{ $t('access_key') }}:
                </td>
                <td>
                  {{ experiment.access_id }}
                </td>
              </tr>
              <tr>
                <td>
                  {{ $t('folder') }}:
                </td>
                <td>
                  {{ experiment.folder_name }}
                </td>
              </tr>
              <tr>
                <td>
                  {{ $t('show_in_ldap_config') }}:
                </td>
                <td>
                  {{ experiment.show_in_ldap_config ? $t('yes') : $t('no') }}
                  - <a
                      :href="$url('administration:switch_ldap_inclusion', [experiment.pk])"
                      :title="$t('switch')"
                    >
                      {{ $t('switch') }}
                    </a>
                </td>
              </tr>
            </tbody>
          </table>

        </div>

        <div class="col-12 col-md-4">
          <table>
            <tbody>
              <tr>
                <td>
                  {{ $t('researchers') }}:
                </td>
                <td>
                  <span
                      v-for="(user, index) in experiment.users"
                  >
                        <span v-if="index != 0">, </span>
                        {{ user.fullname }}
                    </span>
                </td>
              </tr>
              <tr>
                <td>
                  {{ $t('date_created') }}:
                </td>
                <td>
                  {{ experiment.date_created | date('YYYY-MM-DD HH:mm') }}
                </td>
              </tr>
              <tr>
                <td>
                  {{ $t('last_upload') }}:
                </td>
                <td>
                  {{ experiment.last_upload | date('YYYY-MM-DD HH:mm') }}
                </td>
              </tr>
              <tr>
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
                      v-if="!experiment.approved"
                      :href="$url('administration:approve', [experiment.pk])"
                      :title="$t('approve')"
                  >
                    {{ $t('approve') }}
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
        yes: "yes",
        no: "no",
        ID: "ID",
        switch: "switch",
        state: "Status",
        num_datapoints: "Data uploaded",
        access_key: "Access key",
        folder: "Folder",
        edit: "Edit experiment",
        approve: "Approve",
        date_created: "Date created",
        last_upload: "Last upload",
        show_in_ldap_config: "In LDAP config",
        researchers: "Researchers",
      },
      nl: {
        yes: "ja",
        no: "nee",
        ID: "ID",
        switch: "switch",
        state: "Status",
        num_datapoints: "Ge-uploade data",
        access_key: "Access key",
        folder: "Map",
        edit: "Wijzig experiment",
        approve: "Keur goed",
        date_created: "Datum aangemaakt",
        last_upload: "Laatse upload",
        show_in_ldap_config: "In LDAP config",
        researchers: "Onderzoekers",
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
      'loaded': false,
      'showControls': true,
      'defaultItemsPerPage': 10,
    };
  },
  mounted() {
    this.$ufl_load(this, this.$url('administration:home_api', []));
  },
}
</script>

<style>
.ufl-details table {
  border-spacing: 5px 0;
}

.icon-edit:before {
  content: "\E905";
}

.icon-approve:before {
  content: "\EA10";
}
</style>