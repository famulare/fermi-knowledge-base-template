# Edge Verb Registry

Canonical verb vocabulary for the knowledge graph (`scripts/kb_graph.py`). Editable; `kb_graph` overlays this onto its built-in defaults. See `contracts/knowledge_graph_design.md` §3. 7 classes: evidential, structural, tension, synthesis, supersession, associative, potential.

## Registry

| canonical_verb | inverse | class | directed |
|---|---|---|---|
| addresses | addressed-by | structural | yes |
| adds-third-position-to | third-position-added-by | tension | yes |
| applies-to | applied-by | structural | yes |
| builds-on | built-on-by | structural | yes |
| challenges | challenged-by | tension | yes |
| coexists-with | coexists-with | tension | no |
| compatible-with | compatible-with | associative | no |
| compensates-for | compensated-by | structural | yes |
| complements | complements | structural | no |
| conflicts-with | conflicts-with | tension | no |
| connects | connects | associative | no |
| consolidates | consolidated-in | synthesis | yes |
| constrains | constrained-by | structural | yes |
| contextualizes | contextualized-by | structural | yes |
| contradicts | contradicts | tension | no |
| contrasts-with | contrasts-with | tension | no |
| could-integrate-with | could-integrate-with | potential | no |
| could-mitigate | could-be-mitigated-by | potential | yes |
| could-synthesize-with | could-synthesize-with | potential | no |
| critiques | critiqued-by | tension | yes |
| cross-domain | cross-domain | associative | no |
| deepens | deepened-by | structural | yes |
| demonstrates | demonstrated-by | evidential | yes |
| diagnoses | diagnosed-by | evidential | yes |
| directs | directed-by | structural | yes |
| documented-in | documents | associative | yes |
| echoed-by | echoes | evidential | yes |
| echoes | echoed-by | evidential | yes |
| empirically-grounds | empirically-grounded-by | evidential | yes |
| enables | enabled-by | structural | yes |
| enriches | enriched-by | structural | yes |
| evolves | evolved-from | structural | yes |
| exemplified-by | exemplifies | evidential | yes |
| exemplifies | exemplified-by | evidential | yes |
| explains | explained-by | evidential | yes |
| extended-by | extends | structural | yes |
| extends | extended-by | structural | yes |
| formalizes | formalized-by | structural | yes |
| frames | framed-by | structural | yes |
| generalizes | specializes | structural | yes |
| grounded-in | grounds | evidential | yes |
| grounds | grounded-in | evidential | yes |
| guided-by | guides | structural | yes |
| guides | guided-by | structural | yes |
| hierarchical-relationship | hierarchical-relationship | structural | no |
| implemented-by | implements | structural | yes |
| implements | implemented-by | structural | yes |
| in-tension-with | in-tension-with | tension | no |
| informs | informed-by | evidential | yes |
| instantiates | instantiated-by | structural | yes |
| intellectual-ancestor | intellectual-descendant | associative | yes |
| interface-of | interface-of | structural | no |
| justified-by | justifies | evidential | yes |
| justifies | justified-by | evidential | yes |
| lacks | lacked-by | tension | yes |
| methodological-context | methodological-context | associative | no |
| mitigated-by | mitigates | structural | yes |
| mitigates | mitigated-by | structural | yes |
| observed-instance | instance-of | evidential | yes |
| operationalized-by | operationalizes | structural | yes |
| operationalizes | operationalized-by | structural | yes |
| predicts | predicted-by | evidential | yes |
| primacy-tension | primacy-tension | tension | no |
| provides-mechanistic-basis | has-mechanistic-basis | evidential | yes |
| provides-molecular-clock-to | derives-molecular-clock-from | evidential | yes |
| reconciled-with | reconciled-with | tension | no |
| refines | refined-by | structural | yes |
| reframes | reframed-by | structural | yes |
| related-to | related-to | associative | no |
| relates-to | related-to | associative | no |
| resolves | resolved-by | tension | yes |
| scope-ambiguity | scope-ambiguity | tension | no |
| self-contradicts | self-contradicts | tension | no |
| shared-architecture | shared-architecture | associative | no |
| shared-framework | shared-framework | associative | no |
| shares-principle | shares-principle | associative | no |
| specializes | generalizes | structural | yes |
| strengthens | strengthened-by | evidential | yes |
| structural-analogy | structural-analogy | associative | no |
| superseded-by | supersedes | supersession | yes |
| supersedes | superseded-by | supersession | yes |
| supported-by | supports | evidential | yes |
| supported-by- | supports | evidential | yes |
| supports | supported-by | evidential | yes |
| synthesized-in | synthesizes | synthesis | yes |
| synthesizes | synthesized-in | synthesis | yes |
| theory-for | has-theory | structural | yes |
| undermines | undermined-by | tension | yes |
| unified-by | unifies | associative | yes |
| unifies | unified-by | associative | yes |
| validated-by | validates | evidential | yes |
| validates | validated-by | evidential | yes |

## Aliases

| alias | canonical |
|---|---|
| compatible | compatible-with |
| connected-cross-domain | cross-domain |
| connected-in | connects |
| connected-to | connects |
| connects-to | connects |
| connects-to-kb-content | connects |
| core-claims-this-framework-formalizes | formalizes |
| could-integrate | could-integrate-with |
| could-synthesize | could-synthesize-with |
| cross-domain-links | cross-domain |
| direct-connections | connects |
| evidence-source | supported-by |
| exemplified | exemplified-by |
| implements-this-framework | implements |
| kb-connections | connects |
| night-science-extensions | related-to |
| operationalised-by | operationalized-by |
| potential-implementation | could-integrate-with |
| provides-molecular-clock | provides-molecular-clock-to |
| related | related-to |
| related-active-models | related-to |
| related-maps | related-to |
| related-models | related-to |
| related-to-kb-content | related-to |
| related-to-other-kb-content | related-to |
| shared-principle | shares-principle |
| superseded | superseded-by |
| supported-by-independent-evidence | supported-by |
| synthesised-in | synthesized-in |
| tension | in-tension-with |
| this-instantiates | instantiates |
| to-existing-kb-content | related-to |
