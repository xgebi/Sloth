import {Component, h, Prop, State} from '@stencil/core';
import {ISlothEditorSectionData} from "../../interfaces/ISlothEditorSectionData";

@Component({
  tag: 'sloth-editor',
  styleUrl: 'sloth-editor.css',
  shadow: true,
})
export class SlothEditor {
  @Prop() title: string;

  @Prop() sections: string;

  @State() sectionsLocal: ISlothEditorSectionData[] = [];

  connectedCallback() {
    this.sectionsLocal = JSON.parse(this.sections);
  }

  render() {
    return (
      <article>
        <header>
          <laber for="title">Title</laber>
          <input id="title" value={this.title} />
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
        <footer>
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
