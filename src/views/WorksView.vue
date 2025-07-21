<script>
import DisplaySection from "../components/DisplaySection.vue";
import LoadArticlesWithCard2 from "../components/LoadArticlesWithCard.vue";
export default {
  name: 'WorksView',
  components: {
    LoadArticlesWithCard2,
    DisplaySection,
  },
};
</script>

<template>
  <DisplaySection/>
  <load-articles-with-card2></load-articles-with-card2>
</template>