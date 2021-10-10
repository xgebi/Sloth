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
    });

    it('Fill Website name field', () => {
        cy.get('#website-name').clear();
        cy.get('#website-name').type('Cypress test');
    });

    it('Fill Website url field', () => {
        cy.get('#website-url').clear();
        cy.get('#website-url').type('http://localhost:8080');
    });

    it('Selects time zone', () => {
        cy.get('#timezone');
    });

    it('Fill Main Language (long) field', () => {
        cy.get('#main-language-long').clear();
        cy.get('#main-language-long').type('English');
    });

    it('Fill Main Language (short) field', () => {
        cy.get('#main-language-short').clear();
        cy.get('#main-language-short').type('en');
    });

    // To do fill form and and submit it

    // it('Should redirect to login in second registration', () => {
    //     cy.visit('http://localhost:5000/registration');
    //     cy.url().should('include', 'login');
    // });
});