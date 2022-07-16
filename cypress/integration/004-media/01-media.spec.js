describe('Media page', () => {
    before(() => {
        Cypress.Cookies.debug(true);
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
        cy.get('#close-button').should('be.visible');
        cy.get('#close-button').click();
        cy.get('dialog').should('not.have.attr', 'open');
    });

    it('Should attach file', () => {
        cy.get('#open-modal').click();
        cy.get('#file-upload')
            .attachFile('sloth-testing-image.png');
    });

    it('Should fill alt', () => {
        cy.get('.alt-input').type('This is alt');
    });

    it('Should upload file', () => {
        cy.get('#upload-button').click();
    });

    it('Should see a new file', () => {
        cy.wait(2000);
        cy.visit('http://127.0.0.1:5000/');
        cy.login();
        cy.get('.top-level a').contains('Media').click();
        cy.get('img').should('be.visible');
        cy.get('img').should('have.attr', 'src', `/site_test/${(new Date()).getFullYear()}/${(new Date()).getMonth() + 1}/sloth-testing-image.png`);
        cy.wait(2000);
    });
});