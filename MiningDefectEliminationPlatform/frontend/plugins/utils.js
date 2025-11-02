export default ({ app, store }, inject) => {
  inject("utils", {
    initArray(size, value = 0) {
      let array = [];
      for (let ii = 0; ii < size; ii++) {
        array[ii] = value;
      }

      return array;
    },
    columniseObjectArray(a) {
      // e.g. [ {a:1, b:2, c:3}, {a:4, b:5, c:6}, {a:7, b:8, c:9} ]
      // ==> [ a: [1,4,7], b: [2,5,8], c: [3,6,9] ]
      if (!a || a.length == 0) return [];

      return Object.assign(
        ...Object.keys(a[0]).map((key) => ({
          [key]: a.map((o) => o[key]),
        }))
      );
    },
    arrayToDict(array, key) {
      return array.reduce((obj, cur) => {
        return { ...obj, [cur[key]]: cur };
      }, {});
    },
    sortDict(obj) {
      return Object.keys(obj)
        .sort()
        .reduce((v, k) => ((v[k] = obj[k]), v), {});
    },
    uniqueList(items, key, allow_null = false) {
      let values = new Set();

      let X = (x) => {
        try {
          return key.split(".").reduce((a, b) => a[b], x);
        } catch {
          return null;
        }
      };

      for (let item of items) {
        let value = X(item);
        if (value != null || allow_null) {
          values.add(value);
        }
      }

      return [...values].sort();
    },
    fuzzySearch(haystack, needle) {
      let ii = 0;
      let n = -1;
      let jj;

      haystack = haystack.toLowerCase();
      needle = needle.toLowerCase();

      for (; (jj = needle[ii++]); ) {
        if (!~(n = haystack.indexOf(jj, n + 1))) {
          return false;
        }
      }
      return true;
    },
    betterSelectFilter(item, search_text, item_text) {
      if (item.header || item.divider) {
        return true;
      }
      return (
        item_text.toLocaleLowerCase().indexOf(search_text.toLocaleLowerCase()) >
        -1
      );
    },
    filteredItems(items, search, keys) {
      if (!search) return items;

      if (!Array.isArray(keys)) {
        keys = [keys];
      }

      search = search.toLowerCase();

      return items.filter((x) =>
        keys.some((key) => {
          try {
            let value = key.split(".").reduce((o, i) => o[i], x);

            return value.toLowerCase().includes(search);
          } catch (e) {
            console.warn(e);
          }
        })
      );
    },
    hexToRgb(hex) {
      let m = hex.match(/^#?([\da-f]{2})([\da-f]{2})([\da-f]{2})$/i);
      return [parseInt(m[1], 16), parseInt(m[2], 16), parseInt(m[3], 16)];
    },
    daysDiff(date, start) {
      start = new Date(start).setHours(0, 0, 0, 0);
      let plan = new Date(date).setHours(0, 0, 0, 0);

      let offset = (plan - start) / (1000 * 60 * 60 * 24);

      return offset;
    },
    scrollToElement(ref_name, context) {
      if (context == null || ref_name == null) return;

      const element = context.$refs[ref_name];
      context.$nextTick(() => {
        if (element) {
          element.scrollIntoView({
            behavior: "smooth",
          });
        }
      });
    },
    getUserName(id) {
      if (!id) {
        return "";
      }
      const users = store.getters["user/getUsers"];
      return users.find((x) => x.id == id)?.name || "";
    },
    getAuthToken() {
      let token = app.$auth.strategy.token.get();
      token = token ? token.substr(7) : null;
      return token;
    },
  });
};
