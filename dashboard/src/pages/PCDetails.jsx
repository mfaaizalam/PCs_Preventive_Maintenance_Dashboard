import { useParams } from "react-router-dom";
import usePCDetail from "../hooks/usePCDetail";
import LoadingState from "../components/common/LoadingState";
import ErrorState from "../components/common/ErrorState";
import PCDetailHeader from "../components/details/PCDetailHeader";
import SpecsPanel from "../components/details/SpecsPanel";
import PCAlertsSection from "../components/details/PCAlertsSection";
import UnexposedSectionsGrid from "../components/details/UnexposedSectionsGrid";

export default function PCDetails() {
  const { agentId } = useParams();
  const { computer, alerts, alertsLimited, error, loading, refresh } = usePCDetail(agentId);

  if (loading) return <LoadingState label="Loading PC details…" />;
  if (error) return <ErrorState error={error} onRetry={refresh} />;
  if (!computer) return <ErrorState error={{ message: "PC not found." }} onRetry={refresh} />;

  return (
    <div className="mx-auto max-w-6xl space-y-6">
      <PCDetailHeader computer={computer} />

      <div className="grid grid-cols-1 gap-6 lg:grid-cols-[1.3fr_1fr]">
        <SpecsPanel computer={computer} />
        <PCAlertsSection alerts={alerts} limited={alertsLimited} />
      </div>

      <UnexposedSectionsGrid />
    </div>
  );
}
