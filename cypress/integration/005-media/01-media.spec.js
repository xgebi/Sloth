describe('Media page', () => {
    before(() => {
        cy.login();
    });

    it('Should navigate to media page', () => {
        cy.get('.top-level a').contains('Media').click();
        cy.get('h1').contains('List of media');
    });
});