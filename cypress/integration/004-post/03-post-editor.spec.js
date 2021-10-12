describe('Post editor', () => {
    before(() => {
        cy.login();
    });

    it('Should navigate to new post', () => {
        cy.get('.top-level a').contains('Add New Post').click();
        cy.get('h1').contains('Add new Post');
    });
});