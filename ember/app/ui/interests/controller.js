import Controller from "@ember/controller";
import { action } from "@ember/object";
import { inject as service } from "@ember/service";
import { restartableTask, lastValue } from "ember-concurrency-decorators";

export default class InterestsController extends Controller {
  @service notification;
  @service store;

  @lastValue("fetchInterestCategories") categories;

  @action onUpdate() {
    this.fetchInterestCategories.perform();
  }

  @restartableTask *fetchInterestCategories() {
    try {
      return yield this.store.findAll("interest-category", {
        include: "interests",
      });
    } catch (error) {
      console.error(error);
      this.notification.danger("ERROR");
    }
  }
}
