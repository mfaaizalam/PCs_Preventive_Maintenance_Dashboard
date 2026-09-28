import AgentControlRow from "./AgentControlRow";

export default function AgentControlTable({ computers, busyId, onPause, onResume }) {
  return (
    <div className="overflow-x-auto rounded-xl2 border border-ink-100 bg-white shadow-card">
      <table className="w-full min-w-[560px] px-4 text-left">
        <thead>
          <tr className="border-b border-ink-100 text-[11px] uppercase tracking-wide text-ink-300">
            <th className="px-4 py-3 font-medium">PC</th>
            <th className="px-4 py-3 font-medium">Connection</th>
            <th className="px-4 py-3 font-medium">Agent</th>
            <th className="px-4 py-3 font-medium text-right">Action</th>
          </tr>
        </thead>
        <tbody>
          {computers.map((computer) => (
            <AgentControlRow
              key={computer.id}
              computer={computer}
              busy={busyId === computer.id}
              onPause={() => onPause(computer)}
              onResume={() => onResume(computer)}
            />
          ))}
        </tbody>
      </table>
    </div>
  );
}