import {
  Container,
  Heading,
  SkeletonText,
  Table,
  TableContainer,
  Tbody,
  Td,
  Th,
  Thead,
  Tr,
} from "@chakra-ui/react";
import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createFileRoute, Router, useNavigate } from "@tanstack/react-router";
import { useEffect } from "react";
import { z } from "zod";

import { ProjectsService, UsersService } from "../../client/index.ts";
import ActionsMenu from "../../components/Common/ActionsMenu.tsx";
import Navbar from "../../components/Common/Navbar.tsx";
import AddItem from "../../components/Items/AddProject.tsx";
import { PaginationFooter } from "../../components/Common/PaginationFooter.tsx";
import "./layout.css";
import useAuth from "../../hooks/useAuth.ts";
const itemsSearchSchema = z.object({
  page: z.number().catch(1),
});

export const Route = createFileRoute("/_layout/projects")({
  component: Projects,
  validateSearch: (search) => itemsSearchSchema.parse(search),
});

const PER_PAGE = 5;

function getProjectsQueryOptions({ page, id }: { page: number; id: string }) {
  console.log(id);
  return {
    queryFn: () =>
      ProjectsService.readProjects({
        id: id,
        skip: (page - 1) * PER_PAGE,
        limit: PER_PAGE,
      }),
    queryKey: ["users", { page }],
  };
}

function ProjectsTable() {
  const queryClient = useQueryClient();
  const { page } = Route.useSearch();
  const navigate = useNavigate({ from: Route.fullPath });
  const setPage = (page: number) =>
    navigate({
      search: (prev: { [key: string]: string }) => ({ ...prev, page }),
    });
  const { getUserId } = useAuth();
  const userId = getUserId()!;
  const {
    data: projects,
    isPending,
    isPlaceholderData,
  } = useQuery({
    ...getProjectsQueryOptions({ page, id: userId }),
    placeholderData: (prevData) => prevData,
  });

  const hasNextPage = !isPlaceholderData && projects?.data.length === PER_PAGE;
  const hasPreviousPage = page > 1;

  useEffect(() => {
    if (hasNextPage) {
      queryClient.prefetchQuery(
        getProjectsQueryOptions({ page: page + 1, id: userId })
      );
    }
  }, [page, queryClient, hasNextPage]);

  const navigateRouteTask = useNavigate();
  const navigateToTask = (prjId: string) =>
    navigateRouteTask({ to: "/tasks", search: { id: prjId } });

  return (
    <>
      <TableContainer>
        <Table size={{ base: "sm", md: "md" }}>
          <Thead>
            <Tr>
              <Th>Name</Th>
              <Th>Description</Th>
              <Th>Actions</Th>
            </Tr>
          </Thead>
          {isPending ? (
            <Tbody>
              <Tr>
                {new Array(4).fill(null).map((_, index) => (
                  <Td key={index}>
                    <SkeletonText noOfLines={1} paddingBlock="16px" />
                  </Td>
                ))}
              </Tr>
            </Tbody>
          ) : (
            <Tbody>
              {projects?.data.map((project) => (
                <Tr
                  key={project.id}
                  opacity={isPlaceholderData ? 0.5 : 1}
                  onClick={() => navigateToTask(project.id)}
                >
                  <Td isTruncated minWidth="150px">
                    {project.name}
                  </Td>
                  <Td
                    color={!project.description ? "ui.dim" : "inherit"}
                    isTruncated
                    minWidth="150px"
                  >
                    {project.description || "N/A"}
                  </Td>
                  <Td>
                    <div
                      onClick={(event) => {
                        event.preventDefault();
                        event.stopPropagation();
                      }}
                    >
                      <ActionsMenu type={"Project"} value={project} />
                    </div>
                  </Td>
                </Tr>
              ))}
            </Tbody>
          )}
        </Table>
      </TableContainer>
      <PaginationFooter
        page={page}
        onChangePage={setPage}
        hasNextPage={hasNextPage}
        hasPreviousPage={hasPreviousPage}
      />
    </>
  );
}

function Projects() {
  return (
    <Container maxW="full">
      <Heading size="lg" textAlign={{ base: "center", md: "left" }} pt={12}>
        Projects Management
      </Heading>

      <Navbar type={"Item"} addModalAs={AddItem} />
      <ProjectsTable />
    </Container>
  );
}
