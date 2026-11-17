/**
 * RSVP counter for the Rajendra weds Chanda invitation.
 *
 * Paste this whole file into Extensions > Apps Script of a NEW Google Sheet, then
 * Deploy > New deployment > Web app > Execute as: Me, Who has access: Anyone.
 * Copy the web-app URL into rsvp-config.js. Full steps are in README.md.
 *
 * The sheet gets one row per device (guest's phone/browser), so tapping twice or changing
 * the answer never counts twice. Yes / No totals are shown in cells G2 and G3 of the RSVP tab.
 */
var SHEET_NAME = 'RSVP';

function getSheet_() {
  var ss = SpreadsheetApp.getActiveSpreadsheet();
  var sh = ss.getSheetByName(SHEET_NAME);
  if (!sh) {
    sh = ss.insertSheet(SHEET_NAME);
    sh.appendRow(['Device ID', 'Answer', 'First tapped', 'Last changed']);
    sh.setFrozenRows(1);
    sh.getRange('F1:G1').setValues([['Totals', '']]);
    sh.getRange('F2:G3').setValues([
      ['Coming (Yes)', '=COUNTIF(B:B,"yes")'],
      ['Not coming (No)', '=COUNTIF(B:B,"no")']
    ]);
    sh.getRange('A1:G1').setFontWeight('bold');
    sh.setColumnWidth(1, 220);
    sh.setColumnWidth(3, 160);
    sh.setColumnWidth(4, 160);
    sh.setColumnWidth(6, 140);
  }
  return sh;
}

function counts_(sh) {
  var yes = 0, no = 0, last = sh.getLastRow();
  if (last > 1) {
    var vals = sh.getRange(2, 2, last - 1, 1).getValues();
    for (var i = 0; i < vals.length; i++) {
      if (vals[i][0] === 'yes') yes++;
      else if (vals[i][0] === 'no') no++;
    }
  }
  return { yes: yes, no: no };
}

function json_(obj) {
  return ContentService.createTextOutput(JSON.stringify(obj)).setMimeType(ContentService.MimeType.JSON);
}

// Read the totals (the invitation calls this when it opens).
function doGet() {
  var c = counts_(getSheet_());
  return json_({ ok: true, yes: c.yes, no: c.no });
}

// Save one guest's answer: body is {"id": "<device id>", "answer": "yes" | "no"}.
function doPost(e) {
  var lock = LockService.getScriptLock();
  lock.waitLock(20000);
  try {
    var d = JSON.parse(e.postData.contents);
    var id = String(d.id || '').slice(0, 64);
    var answer = d.answer === 'yes' ? 'yes' : (d.answer === 'no' ? 'no' : '');
    if (!id || !answer) return json_({ ok: false, error: 'bad request' });

    var sh = getSheet_();
    var now = new Date();
    var last = sh.getLastRow(), row = -1;
    if (last > 1) {
      var ids = sh.getRange(2, 1, last - 1, 1).getValues();
      for (var i = 0; i < ids.length; i++) {
        if (ids[i][0] === id) { row = i + 2; break; }
      }
    }
    if (row > 0) {
      sh.getRange(row, 2).setValue(answer);
      sh.getRange(row, 4).setValue(now);
    } else {
      sh.appendRow([id, answer, now, now]);
    }
    var c = counts_(sh);
    return json_({ ok: true, yes: c.yes, no: c.no });
  } catch (err) {
    return json_({ ok: false, error: String(err) });
  } finally {
    lock.releaseLock();
  }
}
