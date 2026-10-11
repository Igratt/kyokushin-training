import { useState, type ChangeEvent, type CSSProperties } from 'react';
import type { Program, Settings } from '../types';
import { BUILTIN_PROGRAMS, normalizeProgram, programStats } from '../data/programs';
import { useInstallPrompt } from '../hooks';
import { isNative, nativeTimer } from '../native';
import { Confirm, TopBar } from '../ui';

interface Props {
  programs: Program[];
  program: Program;
  settings: Settings;
  historyCount: number;
  onSettings: (s: Settings) => void;
  onSelectProgram: (id: string) => void;
  onImportProgram: (p: Program) => void;
  onDeleteProgram: (id: string) => void;
  onExportBackup: () => void;
  onImportBackup: (raw: unknown) => string;
  onToast: (text: string) => void;
  onBack: () => void;
}

async function readJson(e: ChangeEvent<HTMLInputElement>): Promise<unknown> {
  const file = e.target.files?.[0];
  e.target.value = '';
  if (!file) throw new Error('');
  const text = await file.text();
  try {
    return JSON.parse(text) as unknown;
  } catch {
    throw new Error('Failas nėra tinkamas JSON.');
  }
}

export default function SettingsScreen(p: Props) {
  const [programError, setProgramError] = useState('');
  const [backupError, setBackupError] = useState('');
  const [confirmDelete, setConfirmDelete] = useState<string | null>(null);
  const [iosHint, setIosHint] = useState(false);
  const install = useInstallPrompt();

  const importProgram = async (e: ChangeEvent<HTMLInputElement>) => {
    setProgramError('');
    try {
      const raw = await readJson(e);
      let prog = normalizeProgram(raw, 'imported');
      if (BUILTIN_PROGRAMS.some((b) => b.id === prog.id)) prog = { ...prog, id: prog.id + '-ikelta' };
      p.onImportProgram(prog);
    } catch (err) {
      const msg = (err as Error).message;
      if (msg) setProgramError(msg);
    }
  };
  const importBackup = async (e: ChangeEvent<HTMLInputElement>) => {
    setBackupError('');
    try {
      p.onToast(p.onImportBackup(await readJson(e)));
    } catch (err) {
      const msg = (err as Error).message;
      if (msg) setBackupError(msg);
    }
  };

  return (
    <div className="screen settings-screen">
      <TopBar
        left={
          <button className="btn-icon" onClick={p.onBack} aria-label="Atgal">
            ‹
          </button>
        }
        center={<span className="top-ex">Nustatymai</span>}
      />

      <section className="settings-section">
        <h2 className="section-title">Programa</h2>
        <p className="muted small">Pasirinkta programa rodoma pradžios ekrane. Pradėta treniruotė tęsiasi su ta programa, su kuria pradėjai.</p>
        <div className="program-list">
          {p.programs.map((prog) => {
            const on = prog.id === p.program.id;
            const color = prog.days[0]?.color ?? '#3B82F6';
            return (
              <div key={prog.id} className={'program-card' + (on ? ' on' : '')} style={{ '--day': color } as CSSProperties}>
                <button className="program-pick" onClick={() => p.onSelectProgram(prog.id)} aria-pressed={on}>
                  <span className="radio" aria-hidden="true" />
                  <span className="program-body">
                    <span className="program-name">
                      {prog.programName}
                      {prog.source === 'imported' && <span className="badge">įkelta</span>}
                    </span>
                    {(prog.focus || prog.goal) && <span className="muted small">{prog.focus ?? prog.goal}</span>}
                    <span className="muted small">{programStats(prog)}</span>
                  </span>
                </button>
                {prog.source === 'imported' &&
                  (confirmDelete === prog.id ? (
                    <Confirm
                      text={`Ištrinti programą „${prog.programName}“? Istorija lieka.`}
                      yes="Ištrinti"
                      no="Ne"
                      danger
                      onYes={() => {
                        setConfirmDelete(null);
                        p.onDeleteProgram(prog.id);
                      }}
                      onNo={() => setConfirmDelete(null)}
                    />
                  ) : (
                    <button className="link-mini program-del" onClick={() => setConfirmDelete(prog.id)}>
                      ištrinti
                    </button>
                  ))}
              </div>
            );
          })}
        </div>
        <label className="btn btn-outline file-btn">
          Įkelti programą iš failo (.json)
          <input type="file" accept=".json,application/json" hidden onChange={importProgram} />
        </label>
        {programError && <div className="error-text">{programError}</div>}
        <p className="muted small">
          Formatas toks pat kaip workout_data.json: programName, goal, days[] su id, name, subtitle ir exercises[] (name, sets, reps, restSeconds,
          description, image).
        </p>
      </section>

      <section className="settings-section">
        <h2 className="section-title">Signalas po poilsio</h2>
        <label className="switch">
          <input type="checkbox" checked={p.settings.sound} onChange={(e) => p.onSettings({ ...p.settings, sound: e.target.checked })} />
          Garsas
        </label>
        <label className="switch">
          <input type="checkbox" checked={p.settings.vibrate} onChange={(e) => p.onSettings({ ...p.settings, vibrate: e.target.checked })} />
          Vibracija
        </label>
        <p className="muted small">
          {nativeTimer
            ? 'Poilsio laikas matosi pranešimuose, o signalas skamba ir kai programa paslėpta.'
            : isNative
              ? 'Įdiek naujausią programos APK, kad poilsio laikas matytųsi pranešimuose ir signalas skambėtų, kai programa paslėpta.'
              : 'Naršyklėje signalas skamba tik kai programa atidaryta.'}
        </p>
      </section>

      <section className="settings-section">
        <h2 className="section-title">Duomenys</h2>
        <p className="muted small">Istorijoje: {p.historyCount} treniruočių. Kopija (.json) perkelia istoriją ir įkeltas programas į kitą telefoną.</p>
        <div className="row wrap">
          <button className="btn btn-outline" onClick={p.onExportBackup}>
            Atsisiųsti kopiją
          </button>
          <label className="btn btn-outline file-btn">
            Įkelti kopiją
            <input type="file" accept=".json,application/json" hidden onChange={importBackup} />
          </label>
        </div>
        {backupError && <div className="error-text">{backupError}</div>}
      </section>

      {!isNative && !install.isStandalone && (
        <section className="settings-section">
          <h2 className="section-title">Programėlė</h2>
          {install.canInstall ? (
            <button className="btn btn-outline" onClick={install.promptInstall}>
              Įdiegti programėlę į telefoną
            </button>
          ) : install.isIOS ? (
            <>
              <button className="btn btn-outline" onClick={() => setIosHint((v) => !v)}>
                Kaip įsidėti į pradžios ekraną
              </button>
              {iosHint && <p className="muted small">Safari: „Dalintis“ → „Į pradžios ekraną“.</p>}
            </>
          ) : (
            <p className="muted small">Android programa: github.com/Igratt/kyokushin-training → Releases → Kyokushin.apk</p>
          )}
        </section>
      )}
    </div>
  );
}
