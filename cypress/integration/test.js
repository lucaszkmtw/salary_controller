describe("Login", () => {
    before(() => {
      cy.fixture("../fixtures/users.json").as("mockedUsers");
    });

    it("Can login through the UI", function () {
      cy.visit("/accounts/login/");
      cy.get("input[name='username']").type(this.mockedUsers[0].fields.email);
      cy.get("input[name='password']").type("dummy_password");
      cy.get("form").submit();
      cy.getCookie("sessionid").should("exist");
    });
  });
