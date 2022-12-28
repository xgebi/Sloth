import {Component, h, Listen, Prop, State} from '@stencil/core';
import {ISlothEditorSectionData} from "../../interfaces/ISlothEditorSectionData";
import {EditorSectionActions} from "../../enums/editor-section-actions";

@Component({
  tag: 'sloth-editor',
  styleUrl: 'sloth-editor.scss',
  shadow: true,
})
export class SlothEditor {
  @Prop() postTitle: string;

  @Prop() sections: string;

  @Prop() mediaList: string;

  @State() sectionsLocal: ISlothEditorSectionData[] = [];

  @Listen('sectionUpdated')
  sectionUpdatedHandler(event: Event) {
    const payload = event["detail"];
    const sectionIndex = this.sectionsLocal.findIndex((item) => item.uuid === payload["uuid"]);
    let arr = this.sectionsLocal;
    switch (payload['action']) {
      case EditorSectionActions.Up:
        if (sectionIndex > 0) {
          [arr[sectionIndex - 1], arr[sectionIndex]] = [arr[sectionIndex], arr[sectionIndex - 1]];
          arr[sectionIndex-1].position -= 1;
          arr[sectionIndex].position += 1;
          this.sectionsLocal = [...arr];
        }
        break;
      case EditorSectionActions.Down:
        if (sectionIndex < this.sectionsLocal.length) {
          [arr[sectionIndex + 1], arr[sectionIndex]] = [arr[sectionIndex], arr[sectionIndex + 1]];
          arr[sectionIndex + 1].position -= 1;
          arr[sectionIndex].position += 1;
          this.sectionsLocal = [...arr];
        }
        break;
      case EditorSectionActions.Delete:
        arr.splice(sectionIndex, 1);
        this.sectionsLocal = [...arr.map((item) => {
          return {
            ...item,
            position: item.position - 1
          };
        })];
        break;
      case EditorSectionActions.TypeChanged:
        arr[sectionIndex].type = payload['data'];
        this.sectionsLocal = [...arr];
        break;
      case EditorSectionActions.ContentChanged:
        arr[sectionIndex].target = payload['data'];
        this.sectionsLocal = [...arr];
        break;
    }
  }

  connectedCallback() {
    this.sectionsLocal = JSON.parse(this.sections);
    console.log(this.sectionsLocal);
  }

  render() {
    return (
      <article class="sloth-editor">
        <header class="sloth-editor__header">
          <laber for="title">Title</laber>
          <input id="title" value={this.postTitle} />
        </header>
          {this.sectionsLocal.map((section) => {
            console.log('se', section, section.original, section.target);
            return (<sloth-editor-section
                type={section.type}
                sectionId={section.uuid}
                position={section.position}
                contentOriginalLanguage={section.original}
                contentTargetLanguage={section.target}
                mediaList={this.mediaList}
              ></sloth-editor-section>)
          })}
        <footer class="sloth-editor__footer">
          <button onClick={this.addSections.bind(this)}>Add section</button>
        </footer>
      </article>
    );
  }

  addSections() {
    const newPosition = this.sectionsLocal.length;
    this.sectionsLocal = [...this.sectionsLocal, {
      target: "",
      original: "",
      position: newPosition,
      type: "text",
      uuid: crypto.randomUUID(),
    }];
  }

}
