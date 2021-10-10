describe('Registration page test', () => {
    it('Should open registration page', () => {
        cy.visit('http://localhost:5000');
    });

    it('Should check registration page is loaded', () => {
        cy.url().should('include', 'registration')
    });

    it('Check h1 & title with text Registration', () => {
        cy.get('h1').should('be.visible');
        cy.get('title').should('contain.text', 'Registration');
    })
});