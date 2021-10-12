describe('Post list', () => {
    before(() => {
        cy.login();
    });

    it('Should navigate to post list', () => {
        cy.get('.top-level a').contains('Post').click();
        cy.get('h1').contains('List of Post');
    });
});