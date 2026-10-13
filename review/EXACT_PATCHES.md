# Exact correction review — https://newstupelo.com

Read-only authenticated preflight. No WordPress writes or media uploads performed.

The JSON receipt binds each post identity, original revision, raw fields and proposed payload to SHA-256 hashes. Any later apply must re-read and compare the full before snapshot; stop on a mismatch or 403. Preserve dates, slugs, authors, statuses, categories, tags, media and all unlisted fields.

## Managed account

{"capabilities": {"edit_others_posts": true, "edit_posts": true, "edit_published_posts": true, "upload_files": true}, "id": 2}

Capability checks support eligibility; actual REST writes are unverified.

## Post 2833

https://newstupelo.com/tupelo-news/auditions-announced-for-live-radio-play-of-a-christmas-carol-2/

- Before snapshot SHA-256: `878c8c178d45dd3ba514f28f6f425afa24e71431f24848ee61dbb76d1dd3c5a0`
- Payload SHA-256: `8e0c2a699626360f60469d54ba81d076421b817e3aeef6718ab33f2e55572971`
- Proposed snapshot SHA-256: `4e354e1d0f7cf03c70a7ff8bc5ee74aa536496c0ab8c5769cfd296ee628d216f`
- Existing author ID: 2; owned by account: True
- Ready: True

### content

```diff
--- before
+++ proposed
@@ -1,3 +1,3 @@
-<p>Theatre Carolina Theatre is holding auditions for a live radio play adaptation of Charles Dickens' classic, "A Christmas Carol." The production aims to bring the holiday story to life through sound effects, multiple characters, and festive spirit.</p> <p>Auditions are scheduled for Oct. 11 at 2 p.m. and Oct. 12 at 6 p.m. They will be held at TCT Off-Broadway, located at 213 East Franklin Street. Participants should arrive prepared with audition material, which will be provided. No previous radio experience is required, only a love for storytelling and a willingness to have fun.</p> <p>The production is seeking five featured actors—three men and two women, ages 20 and up. Additional roles may be available. Performances are set for Dec. 10 to 12. The play will include sound effects and holiday themes, aiming to capture the magic of Christmas.</p> <p>Tickets and further details are available through Theatre Carolina Theatre. The production invites actors of all experience levels to join and help bring this timeless story to life during the holiday season.</p>
+<p>Tupelo Community Theatre scheduled auditions for a live radio play adaptation of Charles Dickens' classic, "A Christmas Carol." The production aims to bring the holiday story to life through sound effects, multiple characters, and festive spirit.</p> <p>Auditions were scheduled for Oct. 11 at 2 p.m. and Oct. 12 at 6 p.m. at TCT Off-Broadway, located at 213 East Franklin Street. The announcement said audition materials would be provided. No previous radio experience is required, only a love for storytelling and a willingness to have fun.</p> <p>The production is seeking five featured actors—three men and two women, ages 20 and up. Additional roles may be available. Performances are set for Dec. 10 to 12. The play will include sound effects and holiday themes, aiming to capture the magic of Christmas.</p> <p>For current production information, see Tupelo Community Theatre’s original announcement. The production invites actors of all experience levels to join and help bring this timeless story to life during the holiday season.</p>
 
 <p><em>Source: <a href="https://www.facebook.com/1458840056250572/posts/1717899780344597" target="_blank" rel="noopener">Original Article</a></em></p>
```

### excerpt

```diff
--- before
+++ proposed
@@ -1 +1 @@
-The TCT Off-Broadway is holding auditions for a live radio adaptation of 'A Christmas Carol,' seeking five featured actors and additional roles.+Tupelo Community Theatre scheduled Oct. 11–12 auditions at TCT Off-Broadway for a live radio adaptation of A Christmas Carol.
```

### Sources and scope

- https://www.facebook.com/1458840056250572/posts/1717899780344597


## Later application boundary

Use the payload digest to bind approved JSON and the before-snapshot digest to detect concurrent edits. The proposed-snapshot hash is a planning fingerprint, not the expected live rendered response: WordPress rendering must be verified separately after any approved write. No apply route exists on this review branch. After approved verified application, retire any one-shot mutation route created for it.
