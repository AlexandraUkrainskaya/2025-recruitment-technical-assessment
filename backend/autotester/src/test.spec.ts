const request = require("supertest");

describe("Task 1", () => {
  describe("POST /parse", () => {
    const getTask1 = async (inputStr) => {
      return await request("http://localhost:8080")
        .post("/parse")
        .send({ input: inputStr });
    };

    it("example1", async () => {
      const response = await getTask1("Riz@z RISO00tto!");
      expect(response.body).toStrictEqual({ msg: "Rizz Risotto" });
    });

    it("example2", async () => {
      const response = await getTask1("alpHa-alFRedo");
      expect(response.body).toStrictEqual({ msg: "Alpha Alfredo" });
    });

    it("error case", async () => {
      const response = await getTask1("");
      expect(response.status).toBe(400);
    });

    it("own test task 1.1", async() => {
        const response = await getTask1("1margharetta_pIzza");
      expect(response.body).toStrictEqual({ msg: "Margharetta Pizza" });
    });
  });
});

describe("Task 2", () => {
  describe("POST /entry", () => {
    const putTask2 = async (data) => {
      return await request("http://localhost:8080").post("/entry").send(data);
    };

    it("Add Ingredients", async () => {
      const entries = [
        { type: "ingredient", name: "Egg", cookTime: 6 },
        { type: "ingredient", name: "Lettuce", cookTime: 1 },
      ];
      for (const entry of entries) {
        const resp = await putTask2(entry);
        expect(resp.status).toBe(200);
        expect(resp.body).toStrictEqual({});
      }
    });

    it("Add Recipe", async () => {
      const meatball = {
        type: "recipe",
        name: "Meatball",
        requiredItems: [{ name: "Beef", quantity: 1 }],
      };
      const resp1 = await putTask2(meatball);
      expect(resp1.status).toBe(200);
    });

    it("Congratulations u burnt the pan pt2", async () => {
      const resp = await putTask2({
        type: "ingredient",
        name: "beef",
        cookTime: -1,
      });
      expect(resp.status).toBe(400);
    });

    it("Congratulations u burnt the pan pt3", async () => {
      const resp = await putTask2({
        type: "pan",
        name: "pan",
        cookTime: 20,
      });
      expect(resp.status).toBe(400);
    });

    it("Unique names", async () => {
      const resp = await putTask2({
        type: "ingredient",
        name: "Beef",
        cookTime: 10,
      });
      expect(resp.status).toBe(200);

      const resp2 = await putTask2({
        type: "ingredient",
        name: "Beef",
        cookTime: 8,
      });
      expect(resp2.status).toBe(400);

      const resp3 = await putTask2({
        type: "recipe",
        name: "Beef",
        cookTime: 8,
      });
      expect(resp3.status).toBe(400);
    });

    it("Unique ingredients", async () => {
        const resp = await putTask2({
        type: "recipe",
        name: "Beef",
        cookTime: 10,
        requiredItems: [{ name: "Beef", quantity: 1 }, {name : "Beef", quantity: 3}, {name: "Pepper", quantity: 1}],
      });
      expect(resp.status).toBe(400);
    })

  });
});

describe("Task 3", () => {
  describe("GET /summary", () => {
    const postEntry = async (data) => {
      return await request("http://localhost:8080").post("/entry").send(data);
    };

    const getTask3 = async (name) => {
      return await request("http://localhost:8080").get(
        `/summary?name=${name}`
      );
    };

    it("What is bro doing - Get empty cookbook", async () => {
      const resp = await getTask3("nothing");
      expect(resp.status).toBe(400);
    });

    it("What is bro doing - Get ingredient", async () => {
      const resp = await postEntry({
        type: "ingredient",
        name: "beef",
        cookTime: 2,
      });
      expect(resp.status).toBe(200);

      const resp2 = await getTask3("beef");
      expect(resp2.status).toBe(400);
    });

    it("Unknown missing item", async () => {
      const cheese = {
        type: "recipe",
        name: "Cheese",
        requiredItems: [{ name: "Not Real", quantity: 1 }],
      };
      const resp1 = await postEntry(cheese);
      expect(resp1.status).toBe(200);

      const resp2 = await getTask3("Cheese");
      expect(resp2.status).toBe(400);
    });

    it("Bro cooked", async () => {
      const meatball = {
        type: "recipe",
        name: "Skibidi",
        requiredItems: [{ name: "Bruh", quantity: 1 }],
      };
      const resp1 = await postEntry(meatball);
      expect(resp1.status).toBe(200);

      const resp2 = await postEntry({
        type: "ingredient",
        name: "Bruh",
        cookTime: 2,
      });
      expect(resp2.status).toBe(200);

      const resp3 = await getTask3("Skibidi");
      expect(resp3.status).toBe(200);
      expect(resp3.body).toStrictEqual({'name': 'Skibidi', 'cookTime': 2, 'ingredients': [{'name':'Bruh', 'quantity': 1}]})
      })

      ///////////////////////////////////
      it("Test return", async () => {
          const meatball = {
              type: "recipe",
               name: "Skibidi2",
        requiredItems: [{ name: "Bruh2", quantity: 2 }],
      };
      const resp1 = await postEntry(meatball);
      expect(resp1.status).toBe(200);
      const bruh = {
              type: "recipe",
               name: "Bruh2",
        requiredItems: [{ name: "Banana2", quantity: 2 }],
      };
      const resp2 = await postEntry(bruh);
      expect(resp2.status).toBe(200);

      const banana = {
              type: "ingredient",
               name: "Banana2",
        cookTime: 1
      };
      const resp3 = await postEntry(banana);
      expect(resp3.status).toBe(200);

      const resp4 = await getTask3("Skibidi2");
      expect(resp4.status).toBe(200)
      expect(resp4.body).toStrictEqual({
          "name": "Skibidi2",
          "cookTime": 4,
          "ingredients": [{"name": "Banana2", "quantity": 4}]
          });
    });

    it("Test return 3", async() => {
        const meatball = {
              type: "recipe",
               name: "Meat Ball 2",
        requiredItems: [{ name: "Sauce 1", quantity: 2 }, {name: 'Sauce 2', quantity: 1}],
      };
      const resp1 = await postEntry(meatball);
      expect(resp1.status).toBe(200);

      const tomato_sauce = {
              type: "recipe",
               name: "Sauce 1",
        requiredItems: [{name: 'Tomato', quantity: 2}],
      };
      const resp2 = await postEntry(tomato_sauce);
      expect(resp2.status).toBe(200);

    const tomato_sauce2 = {
              type: "recipe",
               name: "Sauce 2",
        requiredItems: [{name: 'Tomato', quantity: 3}],
      };
      const resp3 = await postEntry(tomato_sauce2);
      expect(resp3.status).toBe(200);

    const tomato = {
              type: "ingredient",
               name: "Tomato",
               cookTime: 1,
      };
      const resp4 = await postEntry(tomato);
      expect(resp4.status).toBe(200);

    const resp5 = await getTask3("Meat Ball 2");
      expect(resp5.status).toBe(200)
      expect(resp5.body).toStrictEqual({
          "name": "Meat Ball 2",
          "cookTime": 7,
          "ingredients": [{"name": "Tomato", "quantity": 7}]
          });

    })

  });
});
