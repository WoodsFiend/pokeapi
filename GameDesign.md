# Daemonarium
### Game Design Document

**Genre:** Creature-Collection RPG, Turn-Based Combat, Fantasy Adventure  
**Perspective:** Top-Down  
**Setting:** A supernatural world inhabited by powerful, intelligent spirits  
**Core Themes:** Binding, identity, trust, power, evolution, and the consequences of control

---

## 1. Game Overview

**Daemonarium** is a top-down, turn-based creature-collection RPG in which aspiring magicians explore a supernatural world, battle mysterious entities, and form magical contracts with the beings they encounter.

Magicians call these entities *daemons*. The entities themselves, however, prefer to be called *spirits*.

This difference in terminology reflects one of the central tensions of the setting: humans classify supernatural beings according to their own systems of magical knowledge, while spirits possess their own identities, personalities, histories, and ambitions.

Players explore unfamiliar territories, encounter wild spirits, defeat them in battle, and attempt to bind them through magical contracts. Bound spirits become companions in battle, gaining experience, learning new abilities, and evolving into more powerful classifications.

But binding a spirit is not a permanent guarantee of loyalty.

Every ordinary contract is vulnerable to deterioration. Repeated battles, defeat, and fainting weaken the magical bond between magician and spirit. If a contract collapses entirely, the spirit becomes free and escapes. The magician must then locate the escaped spirit at a special reclamation site and attempt to establish a new contract before the opportunity is lost forever.

The exception is the **Soul Bound**: one spirit chosen by the player to receive a unique, permanent safeguard against contract deterioration.

Daemonarium combines familiar turn-based creature battles with a more consequential relationship-management system. The player is not merely collecting creatures; they are maintaining a network of magical agreements with individual supernatural beings.

### Design Pillars

1. **Discover unique spirits.** Encounter a vast variety of supernatural creatures with distinct appearances, attributes, abilities, and personalities.
2. **Master turn-based combat.** Use elemental affinities, tactical moves, status effects, switching, and items to defeat increasingly powerful opponents.
3. **Build lasting relationships.** Bind spirits, develop their abilities, and protect valuable companions from losing their contracts.
4. **Accept meaningful risks.** Defeat and fainting have consequences beyond losing a battle, and a broken contract can ultimately result in permanent loss.
5. **Explore a mysterious world.** Discover new spirits, magical locations, artifacts, and fragments of knowledge about the relationship between magicians and the spirit world.

---

## 2. The World and Its Lore

### 2.1 The Nature of Daemons

Spirits are supernatural beings that exist beyond the ordinary human world. They vary enormously in appearance, intelligence, temperament, and power.

Some resemble familiar animals or fantastical creatures. Others possess elemental bodies, strange anatomies, or forms that appear to defy the physical laws of the world.

Despite their differences, spirits share one important characteristic: they are individuals.

A spirit is more than its classification, elemental affinity, or combat statistics. Each individual can possess a distinct identity, history, personality, and progression.

Magicians generally refer to spirits as *daemons*, a term embedded in magical scholarship and traditional systems of classification. Spirits often reject this terminology because it reduces them to objects of study or control.

This disagreement establishes an underlying question throughout the game:

**Does a magical contract create a partnership, establish ownership, or merely impose a temporary arrangement between two beings?**

The game need not provide a single universal answer. Different magicians, spirits, institutions, and cultures may have different beliefs.

### 2.2 The Magicians

Magicians are humans who have learned to perceive, confront, and bind supernatural entities.

Their abilities allow them to challenge spirits in combat and establish contracts that permit those beings to accompany them into the human world or other dangerous territories.

Magical knowledge is accumulated through experience, study, experimentation, and encounters with spirits. A magician's effectiveness depends not only on personal skill but also on the spirits they have successfully bound and trained.

Binding is not necessarily equivalent to friendship. Some contracts may be mutually beneficial, while others may be maintained through magical coercion, negotiation, or necessity.

This creates room for a world with competing magical traditions, institutions, philosophies, and attitudes toward spirits.

### 2.3 The Spirit World

The supernatural world is divided into regions inhabited by different kinds of spirits.

These regions may contain ancient ruins, dangerous territories, magical phenomena, and places where the boundary between the human world and the spirit world becomes unusually thin.

The origins and full nature of this world are not necessarily understood by humans. Much of what magicians believe about it comes from old texts, classifications, incomplete observations, and the accounts of spirits themselves.

Exploration allows the player to discover new territories and challenge established assumptions about supernatural beings.

### 2.4 The Daemonarium

The name *Daemonarium* evokes a repository or collection devoted to the study of daemons.

Within the setting, it could refer to an institution, a body of magical knowledge, a catalogue of known spirits, or a broader scholarly tradition.

A Daemonarium might contain records of discovered species, classifications, magical abilities, binding techniques, and accounts of individual spirits.

However, no catalogue can completely describe a living spirit. The knowledge collected by magicians is always incomplete, and some spirits may possess abilities, histories, or identities that challenge existing classifications.

This concept can tie the game's title directly to its creature-collection mechanics and its central tension between classification and individuality.

---

## 3. Spirit Classifications and Evolution

Spirits are grouped into classifications that broadly indicate their magical development and potential power.

The current working progression is:

1. **Imp**
2. **Foliot**
3. **Djinn**
4. **Afrit**
5. **Marid**

These classifications provide a framework for progression, encounter difficulty, and the generation of new spirits.

They are not necessarily rigid descriptions of personality or intelligence. Two spirits of the same classification may look and behave very differently.

*Note: These classification names are drawn from existing folklore and the Bartimaeus books. For a commercial release, developing original terminology would help establish a more independent identity for Daemonarium.*

### 3.1 Evolution

Spirits evolve as they gain experience and meet progression requirements.

Evolution represents a meaningful change in the spirit's supernatural capabilities, appearance, and classification.

For example, an individual might begin as an Imp and eventually evolve into a Foliot, later progressing through the remaining classifications.

Evolution should preserve the individual's identity rather than create an unrelated creature.

The evolved spirit retains its accumulated history, learned moves, and established individuality. Its new form represents the continuation of the same being.

### 3.2 Preserving Identity

Each spirit is a persistent individual with its own generated characteristics.

Its identity can include:

- Name and personality.
- Classification and evolutionary history.
- Appearance and recognizable visual features.
- Combat statistics and elemental affinities.
- Ability and learned moves.
- Level and progression history.
- Contract history and other relevant events.

Evolution changes the spirit's form without erasing its past.

When generating artwork for a new evolutionary stage, the system should use the previous appearance as a reference. The resulting design should retain recognizable features while reflecting the spirit's increased power and new classification.

### 3.3 Learning Moves

Spirits learn new moves as they level up.

Moves are selected from valid pools based on the spirit's classification, elemental affinities, and progression rules.

A spirit can maintain up to four active moves at a time. When it learns another move, the player chooses whether to replace an existing move or decline the new one.

Evolution does not automatically reset or replace the spirit's learned moves.

---

## 4. Procedural Spirit Generation

Daemonarium is designed to support a large and potentially expandable variety of spirits without requiring every creature to be manually authored.

The generation system combines controlled game data with AI-generated artwork.

### 4.1 Generated Individual Spirits

Wild spirits are created from valid combinations of characteristics, which may include:

- Classification.
- Elemental affinity or type combination.
- Base statistics and growth characteristics.
- Abilities.
- Eligible move pools.
- Name and personality.
- Visual design.
- Individual history or descriptive details.

The game rules determine which combinations are valid. AI is used primarily to generate artwork and, where appropriate, assist with descriptive content.

AI-generated images should not independently determine gameplay balance. Stats, abilities, moves, and evolution rules must remain within the game's defined constraints.

### 4.2 Visual Consistency

A spirit's artwork should remain consistent with its underlying identity.

The system should support:

- A recognizable front-facing or battle appearance.
- A rear-facing appearance where needed for exploration or battle presentation.
- Consistent visual characteristics across different views.
- Reference-guided artwork for evolutionary forms.
- Clear silhouettes and readable designs at gameplay resolution.

The intention is to create the feeling of discovering many different supernatural individuals while preserving enough consistency that each one remains recognizable.

### 4.3 Rarity and Distribution

Spirit generation can be influenced by location, classification, and encounter conditions.

Some combinations may be common in a region, while others may be rare or associated with unusual environments.

Higher classifications should generally be more difficult to defeat and bind, although classification alone does not need to determine every aspect of a spirit's combat strength.

The encounter system should ensure that generated spirits remain compatible with the game's progression and difficulty rules.

---

## 5. Exploration

The player explores the world from a top-down perspective.

Exploration is the primary way to discover new spirits, find resources, uncover magical knowledge, and access new areas.

### 5.1 Spirit Grass

Tall patches of **Spirit Grass** are visible indicators of supernatural activity.

Entering these areas initiates a wild encounter. The player chooses when to engage by entering the encounter zone rather than being forced into a battle simply by walking through the world.

Spirit Grass provides a recognizable gameplay signal while allowing players to control their exploration pace.

### 5.2 Regional Encounters

Different regions can support different encounter distributions.

The spirits found in an area may depend on:

- Region and environment.
- Local supernatural activity.
- Spirit classification.
- Time of day.
- Magical weather or other environmental conditions, if implemented.

This encourages exploration and gives individual areas a distinct identity.

### 5.3 Exploration Rewards

Exploration may reward the player with:

- Encounters with unfamiliar spirits.
- Magical artifacts and consumable items.
- Binding items and contract restoration supplies.
- Records of previously unknown spirits.
- Access to new regions.
- Lore, puzzles, and other discoveries.

The supernatural world should feel like a place worth exploring independently of the battle system.

---

## 6. Turn-Based Combat

Daemonarium uses a familiar creature-based, turn-by-turn battle structure.

Combat is intended to be approachable, tactical, and centered on the strengths and weaknesses of individual spirits.

### 6.1 Team Composition

The player can maintain an active team of up to six spirits.

Additional bound spirits can be stored outside the active party.

The player chooses a team suited to the encounters they expect to face, balancing elemental coverage, move variety, individual strengths, and other tactical considerations.

Exactly one active team member must be designated as the player's Soul Bound.

### 6.2 Battle Actions

During battle, the player can use the standard actions of a creature-collection RPG:

- **Fight:** Choose one of the active spirit's available moves.
- **Switch:** Replace the active spirit with another eligible team member.
- **Items:** Use appropriate consumable items.
- **Other actions:** Flee from eligible encounters or use additional actions if supported by the final battle design.

Wild encounters and trainer or magician battles can share the same core combat rules while applying different restrictions where appropriate.

### 6.3 Elemental Types

Spirits have elemental affinities that influence their combat interactions.

Types determine which moves a spirit can learn and how effectively it deals with particular opponents.

The type system should support strategic team building and encourage players to use more than a single powerful spirit.

The exact type list, effectiveness chart, and dual-type rules remain to be defined.

### 6.4 Statistics and Status Effects

Spirits use combat statistics to determine their performance in battle.

These may include health, offensive power, defensive power, and speed, along with any additional attributes established by the final combat model.

Moves can deal damage, alter statistics, inflict status conditions, or provide other tactical effects.

Spirits can lose all their health and faint during battle. Fainting affects the contract system in addition to its normal combat consequences.

### 6.5 Defeat

Defeating an opponent's spirit removes it from the current battle according to the combat rules.

Defeating a wild spirit creates an opportunity to attempt binding.

The player must weigh the benefits of winning against the possibility of damaging their own spirits' contracts during the encounter.

---

## 7. Binding Spirits

Binding is the primary way the player recruits wild spirits.

Instead of using a conventional capture device, the player uses a consumable magical binding item to establish a contract with a defeated spirit.

### 7.1 Binding Attempts

After defeating a wild spirit, the player may attempt to bind it.

Each attempt consumes a binding item, whether the attempt succeeds or fails.

Success is not guaranteed. The probability of establishing a contract depends on factors such as:

- The strength and classification of the target.
- The quality of the binding item.
- Any other binding modifiers defined by the game.

More powerful spirits should generally be more difficult to bind, making stronger or rarer spirits more meaningful acquisitions.

### 7.2 Binding Items

Binding items are consumables with different levels of effectiveness.

Higher-quality items improve the probability of a successful contract, particularly against more powerful spirits.

Players must decide whether to use valuable supplies on a difficult target or attempt to bind it using more readily available items.

### 7.3 Successful Binding

A successfully bound spirit becomes part of the player's collection.

It retains its individual identity and becomes available for training, evolution, and team selection.

Binding does not erase the spirit's individuality. It establishes the magical relationship through which the spirit accompanies the magician.

Whether a particular spirit is cooperative, resentful, curious, or indifferent can be reflected in its personality and descriptive content.

---

## 8. Contract Stability

Every ordinary bound spirit has a contract that can deteriorate over time through combat.

**Contract Stability** represents the integrity of the magical bond between the magician and the spirit.

It is a separate system from the spirit's health.

### 8.1 Contract Deterioration

Contract Stability decreases through battle-related events.

The intended rules are:

- Participating in battles causes contract deterioration.
- Losing a battle causes greater deterioration.
- A spirit fainting causes additional deterioration.
- Ordinary travel does not deteriorate contracts.
- Exploration outside combat does not deteriorate contracts.
- Waiting does not deteriorate contracts.
- Storing a spirit does not deteriorate its contract.

The exact amount of deterioration per event remains a balancing decision.

These rules ensure that contract management is a consequence of combat and risk-taking rather than a passive timer that punishes players for exploring or taking breaks.

### 8.2 Health and Contract Stability Are Separate

Healing a spirit's health does not automatically restore its contract.

Likewise, restoring Contract Stability does not automatically heal the spirit.

This separation is important because the two systems represent different problems:

- **Health** represents the spirit's condition in battle.
- **Contract Stability** represents the strength of the magical agreement that keeps the spirit bound.

Players must manage both.

### 8.3 Contract Restoration Items

Contract Restoration items are rare and expensive consumables that restore a fixed amount of Contract Stability.

Each use restores the same amount, regardless of the spirit's current stability percentage.

For example, an item might restore a fixed number of stability points rather than restoring a percentage of the spirit's missing stability.

These items can be used while travelling, allowing players to maintain vulnerable contracts without needing to return to a specific location.

Their scarcity and cost make restoration an important resource-management decision.

---

## 9. Broken Contracts and Reclamation

When an ordinary spirit's Contract Stability reaches zero, the contract breaks.

The spirit becomes unbound and leaves the player's party.

This is one of the game's most consequential failure states.

### 9.1 Losing a Spirit

A spirit whose contract breaks is no longer available as a normal party member.

The player does not simply retrieve it from storage or automatically re-establish the old contract.

Instead, the spirit escapes into the supernatural world.

The player's next step is to locate it through the game's reclamation system.

### 9.2 Reclamation Locations

Broken contracts can be addressed at a special location dedicated to escaped spirits.

A possible name is the **Hall of Broken Contracts**, although the final name and exact narrative role remain open.

This location provides a way to confront spirits whose previous contracts have collapsed.

Its existence also implies that broken contracts are a recognized problem in magical society, serious enough to warrant a dedicated process for recovering escaped beings.

### 9.3 Reclamation Battles

When the player seeks to reclaim a spirit, they must challenge that same individual in battle.

The spirit is not replaced by a random creature of the same classification.

Its identity and progression remain intact, including its:

- Level and combat statistics.
- Moves and abilities.
- Evolutionary classification.
- Appearance.
- Individual history.

The reclamation battle represents the opportunity to establish a new contract with the escaped spirit.

### 9.4 Rebinding Attempts

After defeating the escaped spirit, the player can attempt to bind it again.

Rebinding attempts are limited.

Each attempt follows the binding system's rules, including the consumption of binding items and the possibility of failure.

If the player exhausts the available reclamation attempts without successfully rebinding the spirit, that individual is permanently lost.

This makes a broken contract more than a temporary inconvenience. It creates a meaningful risk that the player may permanently lose a valued individual.

### 9.5 Successful Reclamation

If rebinding succeeds, the original spirit returns to the player's collection.

It retains its existing identity, progression, moves, abilities, and evolution history.

Reclamation does not create a replacement or reset the individual.

The spirit is the same being the player previously bound, even though the relationship between magician and spirit has been interrupted.

---

## 10. The Soul Bound

The **Soul Bound** is a special designation that protects one spirit from contract failure.

Every player must have exactly one Soul Bound, and that spirit must remain on the active team.

The designation is a safeguard for the player's most valued companion.

### 10.1 Designation Rules

- Exactly one spirit is designated Soul Bound at any time.
- The Soul Bound must be a member of the active team.
- The player can change the designation at any time.
- Changing the designation immediately removes the protection from the previous spirit.
- The previously protected spirit becomes an ordinary bound spirit and is subject to normal contract deterioration.
- The newly designated spirit receives Soul Bound protection.

The designation does not provide a combat bonus.

It does not increase statistics, improve moves, or make the spirit stronger in battle.

Its benefit is entirely related to contract security.

### 10.2 Contract Protection

The Soul Bound's contract never deteriorates.

This protection applies even when the spirit participates in battles, loses battles, or faints.

Its contract cannot break through the ordinary Contract Stability system, and the spirit cannot be permanently lost because of contract failure.

The Soul Bound therefore provides a guaranteed anchor for the player's team.

### 10.3 Strategic Significance

Because only one spirit can be protected, choosing a Soul Bound is meaningful.

A player might protect:

- A favourite individual.
- A rare spirit that would be difficult to replace.
- A spirit with an unusual ability or valuable move combination.
- A long-term companion whose evolutionary journey is especially important.
- A spirit the player simply does not want to risk losing.

Changing the designation allows the player to adapt to their priorities.

However, moving protection to another spirit leaves the previous one vulnerable to the normal contract rules.

The Soul Bound system is intended to create emotional investment without providing a direct combat advantage.

---

## 11. Progression and Party Management

The player's long-term progression revolves around discovering spirits, developing a team, and managing the risks associated with binding.

### 11.1 Level Progression

Spirits gain experience through combat and other progression activities established by the game.

As they level up, their statistics improve and they may learn new moves.

Level progression also contributes to the conditions required for evolution.

### 11.2 Evolutionary Progression

Evolution allows a spirit to advance through its classification stages.

The same individual continues through each stage, preserving its learned moves and history.

Evolutionary artwork must reflect the new form while maintaining recognizable features from the previous stage.

### 11.3 Collection Management

The player can store spirits outside the active team and change party composition as needed.

Stored spirits do not suffer contract deterioration simply because they are not being used.

This lets the player maintain a broader collection without continuously exposing every spirit to contract risk.

The Soul Bound, however, must remain on the active team.

### 11.4 Long-Term Goals

Progression goals may include:

- Discovering every known spirit classification.
- Finding rare or unusual individuals.
- Developing a balanced team.
- Evolving spirits through their full progression.
- Discovering new regions.
- Expanding the player's knowledge of the spirit world.
- Maintaining valuable contracts.
- Recovering spirits whose contracts have broken.

The game should reward both tactical mastery and curiosity.

---

## 12. Items and Economy

Items support combat, binding, exploration, and contract management.

The economy should encourage the player to make meaningful choices about which resources to spend and when.

### 12.1 Binding Supplies

Binding items allow the player to attempt contracts with defeated wild spirits.

Different item qualities provide different probabilities of success.

### 12.2 Contract Restoration

Contract Restoration items repair damaged contracts by restoring a fixed amount of Contract Stability.

These items are rare and expensive relative to ordinary supplies.

### 12.3 Battle Items

Battle items can support the usual creature-RPG mechanics, such as restoring health or addressing status conditions.

The precise catalogue of healing, recovery, and utility items remains to be defined.

### 12.4 Sources of Resources

Potential sources include shops, exploration rewards, quests, battles, and discoveries in the supernatural world.

The economy should create tension between spending resources on immediate progress and preserving supplies for difficult encounters or reclamation attempts.

---

## 13. Optional Worldbuilding and Future Systems

The following ideas could deepen the world but are not required for the core gameplay loop.

### 13.1 Spirit Personalities

Generated spirits may have personalities that influence their descriptions, dialogue, or reactions to events.

Examples include curious, proud, cautious, mischievous, or resentful spirits.

Personality should make individual creatures feel distinct without requiring every trait to alter combat balance.

### 13.2 Spirit History and Memories

A spirit's history could record significant events such as its first binding, major battles, evolutions, or reclamation.

These records reinforce the idea that each spirit is a persistent individual rather than a disposable collection entry.

### 13.3 True Names

True Names could be an aspect of magical lore.

They might represent a deeper identity that ordinary classifications cannot fully capture.

The role of True Names in gameplay—if any—would need to be defined separately rather than assumed to be a required binding mechanic.

### 13.4 Magical Artifacts and Puzzles

Exploration could uncover artifacts, ancient inscriptions, sealed locations, and magical puzzles.

These systems would provide alternatives to combat and reward investigation.

### 13.5 Environmental Variations

Day/night cycles, unusual magical weather, spirit territories, and regional anomalies could influence encounters.

These features would make the world feel dynamic and give players reasons to revisit previously explored locations.

### 13.6 Research and the Daemonarium

A catalogue of discovered spirits could gradually fill with observations, classifications, appearances, and known abilities.

The catalogue might reveal where a spirit has been encountered and which aspects of its nature remain unknown.

This would connect the title directly to exploration and collection without requiring the catalogue to explain everything about every spirit.

---

## 14. Core Gameplay Loop

The central gameplay loop is:

1. **Explore** the world and discover areas with supernatural activity.
2. **Encounter** wild spirits by entering Spirit Grass or other encounter zones.
3. **Battle** using turn-based combat, elemental affinities, moves, and tactical switching.
4. **Bind** defeated spirits using consumable binding items.
5. **Train** spirits through experience, new moves, and improved statistics.
6. **Evolve** individual spirits into more advanced classifications.
7. **Manage contracts** by monitoring Contract Stability and using restoration items.
8. **Protect a Soul Bound** to ensure one active team member is safe from contract failure.
9. **Reclaim escaped spirits** when contracts break, accepting the risk of permanent loss if rebinding fails.
10. **Explore further** to discover stronger spirits, new regions, and more of the world's hidden history.

This loop combines the familiar appeal of collecting and training creatures with a persistent system of risk, resource management, and individual identity.

---

## 15. Design Principles

Daemonarium should follow several principles to keep its systems coherent.

### Individuality Over Replaceability

A generated spirit should feel like a persistent individual. Evolution and reclamation must preserve identity rather than produce a substitute.

### Consequences Without Constant Punishment

Contract deterioration should come from battle-related risk, not simply from time passing. Players should be able to explore, travel, and store spirits without worrying about invisible decay.

### Meaningful Protection

The Soul Bound protects a favourite spirit from contract failure without making it stronger in combat. It offers security rather than power.

### Risk With Recovery Opportunities

A broken contract should be serious, but it should initially create an opportunity for reclamation. Permanent loss occurs only after the player exhausts the limited rebinding attempts.

### Controlled Procedural Generation

AI should increase visual and descriptive variety without undermining gameplay rules. Generated spirits must remain compatible with the established combat, progression, and evolution systems.

### Mystery Without Excessive Explanation

Magicians may possess elaborate classification systems, but their knowledge should not define the entirety of spirit existence. The world should leave room for uncertainty, disagreement, and discovery.

---

## 16. Summary

**Daemonarium** is a creature-collection RPG about magicians who bind supernatural beings known to humans as daemons, but who prefer to call themselves spirits.

Players explore a mysterious world, battle wild spirits, establish magical contracts, train individual creatures, and guide them through successive evolutionary classifications.

Its defining mechanic is Contract Stability: battle-related events can weaken the bond between magician and spirit until the spirit escapes. Players can attempt to reclaim escaped individuals, but failed reclamation attempts may result in permanent loss.

The Soul Bound provides one guaranteed safe companion, protecting that spirit's contract without granting a combat advantage.

Combined with procedurally generated spirits, persistent individual identities, evolution, and a world built around the tension between classification and individuality, Daemonarium aims to make every spirit feel like more than another entry in a collection.

**At its heart, Daemonarium is about the difference between possessing a spirit and forming a lasting bond with one.**