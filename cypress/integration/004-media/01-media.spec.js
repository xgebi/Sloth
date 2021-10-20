describe('Media page', () => {
    before(() => {
        cy.login();
    });

    it('Should navigate to media page', () => {
        cy.get('.top-level a').contains('Media').click();
        cy.get('h1').contains('List of media');
    });

    it('Should open upload dialog', () => {
        cy.get('#open-modal').click();
        cy.get('media-uploader').should('have.length', 1);
        const shadow = cy.get('media-uploader').shadow();
        shadow.find('dialog').should('have.length', 1);
    });

    it('Should close upload dialog', () => {
        const shadow = cy.get('media-uploader').shadow();
        shadow.find('#close-button').click();
        shadow.find('dialog').should('not.have.attr', 'open');
    });

    it('Should attach file', () => {

    });

    it('Should fill alt', () => {

    });

    it('Should upload file', () => {

        cy.reload()
    });

    it('Should see a new file', () => {

    });
});