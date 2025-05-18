describe('Login page spec', () => {
  it('login works', () => {
    cy.visit('http://localhost:3000/login')
    const usernameField = cy.get("#username-field");
    usernameField.focus().type("sarah")

    const passwordField = cy.get("#password-field");
    passwordField.focus().type("cypress")

    const button = cy.get("button");
    button.click();
    cy.wait(1000)
    cy.location('pathname').should('include', '/dashboard')
  })

  it('login should not let in', () => {
    cy.visit('http://localhost:3000/login')
    const usernameField = cy.get("#username-field");
    usernameField.focus().type("sarah")

    const passwordField = cy.get("#password-field");
    passwordField.focus().type("nope")

    const button = cy.get("button");
    button.click();
    cy.wait(1000)
    cy.location('search').should('include', 'error')
    cy.contains('Incorrect credentials')
  })
})