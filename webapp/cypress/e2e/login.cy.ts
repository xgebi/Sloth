describe('template spec', () => {
  it('passes', () => {
    cy.visit('http://localhost:3000/login')
    cy.get("#username-field").focus()
  })
})