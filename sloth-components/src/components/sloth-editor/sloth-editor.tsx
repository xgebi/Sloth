import {Component, h, Prop, State} from '@stencil/core';
import {ISlothEditorSectionData} from "../../interfaces/ISlothEditorSectionData";

@Component({
  tag: 'sloth-editor',
  styleUrl: 'sloth-editor.scss',
  shadow: true,
})
export class SlothEditor {
  @Prop() postTitle: string;

  @Prop() sections: string;

  @State() sectionsLocal: ISlothEditorSectionData[] = [];

  connectedCallback() {
    this.sectionsLocal = JSON.parse(this.sections);
  }

  render() {
    return (
      <article class="sloth-editor">
        <header class="sloth-editor__header">
          <laber for="title">Title</laber>
          <input id="title" value={this.postTitle} />
        </header>
        <div>
          {this.sectionsLocal.map((section) => (<section>
            <sloth-editor-section
              type={section.type}
              contentOriginalLanguage={section.content}
              contentTargetLanguage={section.original}
            ></sloth-editor-section>
          </section>))}
        </div>
        <footer class="sloth-editor__footer">
          <button onClick={this.addSections.bind(this)}>Add section</button>
        </footer>
      </article>
    );
  }

  addSections() {
    const newPosition = this.sectionsLocal.length;
    this.sectionsLocal = [...this.sectionsLocal, {
      content: "",
      original: "",
      position: newPosition,
      type: "text",
      uuid: crypto.randomUUID(),
    }];
  }

}
