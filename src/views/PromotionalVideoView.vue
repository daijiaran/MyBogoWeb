<script>
// import DisplaySection from "../components/DisplaySection.vue";
import LoadArticlesWithCard_UseCateGory from "@/components/Article/LoadArticlesWithCard_UseCateGory.vue";
export default {
  name: 'PromotionalVideo',
  components: {
    LoadArticlesWithCard_UseCateGory,
  },
};
</script>

<template>
<!--  <DisplaySection/>-->
  <LoadArticlesWithCard_UseCateGory :category-id="2" style="padding-top: 80PX"></LoadArticlesWithCard_UseCateGory>

</template>